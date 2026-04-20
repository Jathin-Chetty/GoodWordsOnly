const LABEL_NAMES = {
  LABEL_0: "Appropriate",
  LABEL_1: "Inappropriate",
  LABEL_2: "Offensive",
  LABEL_3: "Violent",
};

function normalizeScores(rawOutput) {
  if (!Array.isArray(rawOutput) || rawOutput.length === 0) {
    throw new Error("Unexpected model response format");
  }

  const scores = Array.isArray(rawOutput[0]) ? rawOutput[0] : rawOutput;
  const normalized = scores
    .filter((item) => item && typeof item === "object" && item.label)
    .map((item) => ({
      label: item.label,
      display_label: LABEL_NAMES[item.label] || item.label,
      score: Number(item.score || 0),
    }))
    .sort((a, b) => b.score - a.score);

  if (normalized.length === 0) {
    throw new Error("Model returned no class scores");
  }

  return normalized;
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
    const text = (body?.text || "").trim();
    if (!text) {
      return res.status(400).json({ error: "Text cannot be empty" });
    }

    const model = process.env.HF_MODEL || "IMSyPP/hate_speech_multilingual";
    const token = process.env.HF_TOKEN || "";
    const endpoint = `https://router.huggingface.co/hf-inference/models/${model}`;

    const headers = { "Content-Type": "application/json" };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const hfResponse = await fetch(endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify({
        inputs: text,
        parameters: {
          top_k: null,
          function_to_apply: "softmax",
        },
      }),
    });

    if (!hfResponse.ok) {
      const message = await hfResponse.text();
      if (hfResponse.status === 401) {
        return res.status(500).json({
          error: "Hugging Face authentication failed. Set HF_TOKEN in Vercel env vars.",
        });
      }
      return res.status(500).json({
        error: `Hugging Face API error (${hfResponse.status}): ${message}`,
      });
    }

    const responseData = await hfResponse.json();
    const classes = normalizeScores(responseData);
    const top = classes[0];

    return res.status(200).json({
      model,
      label: top.label,
      display_label: top.display_label,
      probability: top.score,
      classes,
    });
  } catch (error) {
    return res.status(500).json({ error: error.message || "Internal server error" });
  }
}
