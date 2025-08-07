import json

from openai import OpenAI
from flask import Blueprint,session,request,jsonify

SYSTEM_PROMPT="""
You are an expert resume parser and editor at the Harvard Extension School. You will reply with JSON object only.
"""

BASICS_PROMPT = """
Your task is to extract the applicant's basic information from their CV and rewrite it, if necessary, to better align with the provided job description (JD).

Here is the CV:
<RESUME_FILE>

Here is the target job description:
<TARGET_JD>

Format your output as JSON using the following TypeScript interface:

interface Basics {
    name: string;
    email: string;
    phone: string;
    website: string;
    address: string;
}

Instructions:
- Carefully extract all fields from the CV.
- If the job description specifies or implies preferences for formatting (e.g., location, phone format, website, etc.), adjust the output accordingly.
- Only include fields that can be confidently extracted or inferred; leave other fields as empty strings.
- Output only the JSON object, nothing else.

Now write the basics section:
"""

EDUCATION_PROMPT = """
Your task is to extract the applicant's education information from their CV and rewrite or highlight it, if necessary, to best match the requirements of the target job description (JD).

Here is the CV:
<RESUME_FILE>

Here is the target job description:
<TARGET_JD>

Format your output as JSON using the following TypeScript interface:

interface EducationItem {
    institution: string;
    area: string;
    additionalAreas: string[];
    studyType: string;
    startDate: string;
    endDate: string;
    score: string;
    location: string;
}

interface Education {
    education: EducationItem[];
}

Instructions:
- Extract all relevant education details from the CV.
- If the JD specifies preferred degrees, majors, institutions, or locations, ensure the output highlights or matches these as closely as possible (e.g., use preferred terminology or order).
- For fields not present or unclear in the CV, leave them as empty strings or empty arrays.
- Output only the JSON object, nothing else.

Now write the education section:
"""

AWARDS_PROMPT = """
Your task is to extract the applicant's awards and honors from their CV and present them to best match or highlight the requirements or preferences stated in the target job description (JD).

Here is the CV:
<RESUME_FILE>

Here is the target job description:
<TARGET_JD>

Format your output as JSON using the following TypeScript interface:

interface AwardItem {
    title: string;
    date: string;
    awarder: string;
    summary: string;
}

interface Awards {
    awards: AwardItem[];
}

Instructions:
- Extract all relevant awards and honors from the CV.
- If the JD references specific skills, achievements, or types of recognition, highlight awards most relevant to those requirements (e.g., technical contests for a tech job, or leadership awards for a management role).
- If possible, rewrite titles or summaries to better match the language or focus of the JD.
- For fields not present or unclear in the CV, leave them as empty strings.
- Output only the JSON object, nothing else.

Now write the awards section:
"""

PROJECTS_PROMPT = """
Your task is to extract the applicant's projects from their CV and present them to best match or highlight the requirements and language of the target job description (JD).

Here is the CV:
<RESUME_FILE>

Here is the target job description:
<TARGET_JD>

Format your output as JSON using the following TypeScript interface:

interface ProjectItem {
    name: string;
    keywords: string[];
    highlights: string[];
    url: string;
}

interface Projects {
    projects: ProjectItem[];
}

Instructions:
- Extract all relevant projects from the CV.
- If the JD mentions specific skills, technologies, or domains, highlight or rewrite the most relevant projects to better match those requirements or language.
- Populate the `keywords` field with up to 5 key skills, technologies, or domains for each project.
- Where possible, quantify achievements or impact using numbers, percentages, or other measurable results (e.g., "Improved processing speed by 25%," "Managed a budget of $50,000," "Trained 5 new team members").
- For fields not present or unclear in the CV, leave them as empty strings or empty arrays.
- Output only the JSON object, nothing else.

Now write the projects section:
"""

SKILLS_PROMPT = """
Your task is to extract the applicant's most relevant skills from their CV and present them to best match the requirements and language of the target job description (JD).

Here is the CV:
<RESUME_FILE>

Here is the target job description:
<TARGET_JD>

type HardSkills = "Programming Languages" | "Tools" | "Frameworks" | "Computer Proficiency";
type SoftSkills = "Team Work" | "Communication" | "Leadership" | "Problem Solving" | "Creativity";
type OtherSkills = string;

Now consider the following TypeScript Interface for the JSON schema:

interface SkillItem {
    name: HardSkills | SoftSkills | OtherSkills;
    keywords: string[];
}

interface Skills {
    skills: SkillItem[];
}

Instructions:
- Extract up to the top 4 skill names that are both present in the CV and most relevant to the target JD, prioritizing those that relate to the applicant's education and work experience.
- For each skill, include a `keywords` array with up to 5 related sub-skills, tools, technologies, or concepts, reflecting the JD’s terminology and requirements where possible.
- Use the skill categories provided above, or add relevant custom skills as needed.
- For skills or keywords not clearly present in the CV, leave them as empty strings or omit them.
- Output only the JSON object, nothing else.

Now write the skills section:
"""

WORK_PROMPT = """
Your task is to extract and rewrite the applicant's work experience from their CV, presenting it to best match the requirements and language of the target job description (JD).

Here is the CV:
<RESUME_FILE>

Here is the target job description:
<TARGET_JD>

Now consider the following TypeScript Interface for the JSON schema:

interface WorkItem {
    company: string;
    position: string;
    startDate: string;
    endDate: string;
    location: string;
    highlights: string[];
}

interface Work {
    work: WorkItem[];
}

Instructions:
- Extract only the work experience (do not include project experience) from the CV.
- For each work experience, provide the company name, position name, start and end date, and location.
- Phrase each item in 'highlights' using the STAR (Situation, Task, Action, Result) methodology, following Harvard Extension School Resume guidelines.
- Where possible, quantify achievements or impact using numbers, percentages, or other measurable results (e.g., "Improved processing speed by 25%," "Managed a budget of $50,000," "Trained 5 new team members").
- Where possible, rewrite or emphasize work experiences and highlights to best align with the requirements and preferred terminology in the JD.
- For fields not present or unclear in the CV, leave them as empty strings or empty arrays.
- Output only the JSON object, nothing else.

Now write the work section:
"""



def generate_json_from_extracted_texts(resume_text:str ,jd_text:str )->json:
    sections=[]
    try:
        api_key=session["api_key"]
        client=OpenAI(api_key=api_key)

        counter=1
        for prompt in [BASICS_PROMPT,EDUCATION_PROMPT,AWARDS_PROMPT,PROJECTS_PROMPT,SKILLS_PROMPT,WORK_PROMPT]:
            filled_prompt:str=prompt.replace("<RESUME_FILE>",resume_text).replace("<TARGET_JD>",jd_text)
    
            completion=client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {"role":"developer","content":SYSTEM_PROMPT},
                    {"role":"user","content":filled_prompt}
                ]
            )
            response=completion.choices[0].message.content
            answer=json.loads(response)

            if prompt == BASICS_PROMPT and "basics" not in answer:
                answer = {"basics": answer} # A common mistake GPT would make

            sections.append(answer)
            print(f"{counter}/6 section has completed")
            counter+=1
            
        
        final_answer={}

        for section in sections:
            final_answer.update(section)

        return final_answer
    except Exception as e:
        print(str(e))
        return 

# print(json.dumps(generate_json_from_extracted_texts(resume_text,jd_text)))

