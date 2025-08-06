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

resume_text="""
Lawrence (Zuxin) Xie 
zuxinxie@usc.edu | 626-818-3015 | linkedin.com/in/zuxin-xie-691535327/

EDUCATION
University of Southern California, Viterbi School of Engineering
Master of Science in Analytics (GPA 3.67/4.0)

Los Angeles, CA
        Aug 2024 - May 2026

• Software Engineer passionate about Machine Learning, with hands-on experience in end-to-end ML projects

Shanghai University, School of Communication & Information Engineering
Bachelor of Engineering in Data Science and Big Data Technology

 Shanghai, China
        Sep 2020 - Jun 2024

• Relevant Coursework: Object-Oriented Programming, Algorithms, Data Structures, Machine Learning, Natural

Language Processing, Computer Vision, Operating Systems, Database Management System

TECHNICAL SKILLS

• Programming: Python, C++, SQL, R, HTML, CSS, JavaScript
• SWE Skills: Cloud Deployment, Version Control, REST API, Django, AWS, MySQL, Git, Linux, Docker
• ML Skills: Natural Language Processing, Computer Vision, LLM, PyTorch, Word2Vec, Hugging Face, OpenCV

SOFTWARE ENGINEER EXPERIENCE
FESCO Adecco
Intern, Software Development Engineer

Shanghai, China
                        Jul 2024 - Aug 2024

• Developed and deployed a cloud-based B2B SaaS platform for internal asset management system (Python, Tornado,

MySQL), supporting real-time file operations and secure multi-user access, serving 200+ enterprises users.

• Integrated the backend system into company’s internal server infrastructure with employee-only authentication and

improved system storage logic to reduce storage usage by 30%.

China Telecom
Intern, Machine Learning Engineer

Shanghai, China
Jun 2023 - Aug 2023
• Containerized and deployed a Computer Vision model (YOLO-v8) using Docker on AWS, enabling real-time trash bin

monitoring within existing surveillance software.

• Set up CI/CD pipelines using GitHub actions to streamline testing, containerization and deployment of AI models,

reducing manual workflows by 40%.

Fukan Information Technology Co., Ltd.
Intern, Software Development Engineer

Shanghai, China
Jun 2022 - Aug 2022
• Redesigned database schema (MySQL) by modifying primary key structures and optimized backend order-processing

logic, improving query efficiency by nearly 20%.

• Collaborated with front-end engineers to integrate REST APIs, ensuring seamless data-flow and real-time updates.

MACHINE LEARNING PROJECTS
Weakly-Supervised Instance Segmentation | Computer Vision, BoxInst

 Mar 2024 - Jun 2024

• Collaborated with Nullmax, an autonomous driving company, to train a weakly supervised instance segmentation model

based on BoxInst, reducing manual annotation cost by 40%.

• Created a traffic-scene dataset and implemented data augmentation techniques, leading to a 10% improvement

in both mAP and mIoU on road users (e.g., pedestrians, cars and bikes) after fine-tuning.

Sentiment Classification on TaoBao Reviews | Natural Language Processing, RNN, Word2Vec       Sept 2023 - Nov 2023
• Built a sentiment classification model to classify and extract user feelings from TaoBao review data with three output

classes: positive, negative, and ambiguous, using PyTorch and RNN, achieving 98% average precision.

• Set up and maintained a preprocessing and embedding pipeline for unstructured review text, generating dense

Word2Vec vectors to support downstream sentiment classification and enable semantic understanding of user feedback.

Medical Image Segmentation | Computer Vision, U-Net Model

Mar 2023 - Jun 2023

• Designed and implemented a U-Net architecture to perform pixel-level cell instance segmentation on microscopy

images, improving performance on small, high-density cell clusters.
images, improving performance on small, high-density cell clusters.
images, improving performance on small, high-density cell clusters.

• Achieved a 16% boost in segmentation accuracy over statistical methods like OTSU, and increased processing speed by      

5% on large, isolated cells through optimized architecture and post-processing.
"""

jd_text="""
About the job
"

Reddit is a community of communities where people can dive into anything through experiences built around their interests, hobbies, and passions. Our mission is to bring community, belonging, and empowerment to everyone in the world. Reddit users submit, vote, and comment on content, stories, and discussions about the topics they care about the most. From pets to parenting, there’s a community for everybody on Reddit and with over 50 million daily active uniques, it is home to the most open and authentic conversations on the internet. For more information, visit redditinc.com.

Are you a beginner Software Engineer with a dream of both coding and browsing subreddits at work? Well, you're in the right place! Reddit is in search of a recent graduate interested in Software Engineering and Community Safety to join our Emerging Talent New Graduate program (and we guarantee you'll get to do some of both!).

The Moderation organization’s mission lies at the core of Reddit's success as a platform: we build features that enable moderators to create and grow meaningful, destination communities. Moderators are a key pillar of Reddit’s success, and act as community leaders and tastemakers, ensuring there’s something on Reddit for everyone. With such huge responsibility, it is important that Reddit can empower mods, users, and Reddit to maintain a transparent, sustainable, and adaptable balance of ownership and accountability within their communities. Under this organization pillar, the Moderation Strategy team is focused on delivering automations for Moderators using the latest technologies to help build for the future of Moderation.

Responsibilities

Work on projects that impact the business - The Moderation team is a fullstack focused team - You'll gain exposure to how a real engineering team works, from sprint planning to shipping code (UX, Software Engineering, Data Visualization).

Some previous projects include:
LLM User Summaries - AI-generated summaries of a Reddit user's profile, designed specifically for subreddit moderators.
Automations Platform - a unified, flexible system that streamlines and enhances the tools available to communities for content and user management.
LLM Based Rule Enforcement - system that leverages large language models to help automate the moderation of Reddit communities by evaluating posts against subreddit-specific rules.
Come work at our San Francisco, New York, Chicago or Los Angeles offices - complete with catered lunch Monday-Thursday, free snacks/drinks, and in person events!

Continue making Reddit history as a part of our next New Grad cohort - Be a part of a new community, meet other recent graduates and take part in our New Grad events.

Required Qualifications

Bachelor's degree or higher in a quantitative/CS major (e.g., mathematics, statistics, economics, finance, computer science). 
Graduated between December 2024 and June 2025, with less than 2 years of relevant professional work experience
Strong knowledge of CS fundamentals (able to program your way out of a paper bag) 
Proficiency in at least one or more programming languages such as Java, Python, Golang, C++, etc. 
Experience in full stack engineering, working with a database, social networks, or open source projects

Preferred Qualifications

Excellent verbal and written communication skills 
Experience working at a start-up or mid-sized company
Proficiency in backend languages such as Golang or Python 
Experience in moderating online communities
A desire to work at one of our Reddit office locations (San Francisco, New York City, Chicago or Los Angeles) 

Benefits

Comprehensive Healthcare Benefits
401k Matching
Workspace benefits for your home office
Annual Personal & Professional development funds
Family Planning Support
Flexible Vacation (please use them!) & Reddit Global Snoo (Wellness) Days 
4+ months paid Parental Leave
Paid Volunteer time off

"
"""

def generate_json_from_extracted_texts(resume_text:str =resume_text,jd_text:str =jd_text)->json:
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

