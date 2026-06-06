"""
utils/ai_helpers.py — OpenAI API wrappers for interview analysis and AI summaries
"""
import json
import os
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def analyze_interview_transcript(transcript: str, job_title: str = "") -> dict:
    """
    Send interview transcript to OpenAI and return structured analysis.
    Returns scores + qualitative feedback.
    """
    if not OPENAI_API_KEY:
        return _mock_interview_analysis()

    system_prompt = """You are an expert HR interviewer and talent assessment specialist.
Analyze the provided interview transcript and return ONLY a JSON object with this exact structure:
{
  "communication_score": <float 0-10>,
  "technical_score": <float 0-10>,
  "confidence_score": <float 0-10>,
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendation": "<one of: strong_hire, hire, consider, reject>",
  "detailed_feedback": "<2-3 sentence professional summary>"
}
Be objective and base scores strictly on the transcript content."""

    user_prompt = f"""Job Role: {job_title or 'General Position'}

Interview Transcript:
{transcript[:3000]}

Analyze the candidate's performance and return the JSON assessment."""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        return _mock_interview_analysis()


def generate_resume_summary(resume_text: str, job_description: str) -> str:
    """Generate a short AI summary of how well the resume fits the job."""
    if not OPENAI_API_KEY:
        return "AI summary unavailable — add OPENAI_API_KEY to .env"

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert recruiter. In 2-3 sentences, summarise how well the candidate's resume matches the job description. Be specific about fit.",
                },
                {
                    "role": "user",
                    "content": f"Job Description:\n{job_description[:1000]}\n\nResume:\n{resume_text[:1500]}",
                },
            ],
            max_tokens=200,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "AI summary could not be generated."


def _mock_interview_analysis() -> dict:
    """Fallback when OpenAI key is missing — useful for demos."""
    return {
        "communication_score": 7.2,
        "technical_score": 6.8,
        "confidence_score": 7.5,
        "strengths": ["Clear articulation", "Good technical depth", "Positive attitude"],
        "weaknesses": ["Could improve on system design", "Needs more examples"],
        "recommendation": "hire",
        "detailed_feedback": "The candidate demonstrated solid communication skills and reasonable technical knowledge. They showed enthusiasm for the role and provided coherent answers. Recommended for hire with some onboarding support on system design concepts.",
    }
