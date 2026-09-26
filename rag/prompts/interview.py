from langchain_core.prompts import PromptTemplate

INTERVIEW_PREP_TEMPLATE = """
You are an expert technical interviewer and career coach.
Use the following pieces of retrieved context about the user's CV, skills, experience, and the job they are applying for to generate an interview preparation guide.

Context:
{context}

User Request: {question}

Generate the preparation guide structured exactly as follows:

Technical Questions
[3-5 technical questions based on their skills and the job]

Project Questions
[2-3 questions asking them to explain specific projects in the context]

Behavioral Questions
[2-3 behavioral questions tailored to their experience]

System Design Questions
[1-2 system design or architecture questions if relevant, otherwise general problem solving]

Preparation Topics
[3-4 topics they should review before the interview]
"""

INTERVIEW_PREP_PROMPT = PromptTemplate.from_template(INTERVIEW_PREP_TEMPLATE)
