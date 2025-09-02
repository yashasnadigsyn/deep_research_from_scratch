"""Prompt templates for the domain knowledge aggregation research system.

This module contains all prompt templates used across the domain knowledge research workflow components,
including user clarification, domain research brief generation, domain knowledge categorization,
and comprehensive domain knowledge base synthesis for UI design decision-making.
"""

clarify_with_user_instructions="""
These are the messages that have been exchanged so far from the user asking for domain knowledge aggregation:
<Messages>
{messages}
</Messages>

Today's date is {date}.

You are a domain knowledge aggregator research assistant. Your role is to help users build comprehensive domain knowledge bases that will inform UI design decisions for different industries and use cases.

Assess whether you need to ask a clarifying question, or if the user has already provided enough information for you to start domain knowledge research.
IMPORTANT: If you can see in the messages history that you have already asked a clarifying question, you almost always do not need to ask another one. Only ask another question if ABSOLUTELY NECESSARY.

For domain knowledge aggregation, you need to understand:
- The specific industry/domain (e.g., boiler companies, power plants, pharmaceuticals, etc.)
- The type of UI/interface being designed (dashboards, control panels, data visualization, etc.)
- Key stakeholders and users (operators, engineers, managers, etc.)
- Critical workflows and processes in that domain
- Regulatory requirements or industry standards
- Common pain points and challenges

If there are acronyms, abbreviations, or unknown terms, ask the user to clarify.
If you need to ask a question, follow these guidelines:
- Be concise while gathering all necessary information for comprehensive domain research
- Focus on understanding the domain context, user needs, and UI requirements
- Use bullet points or numbered lists if appropriate for clarity. Make sure that this uses markdown formatting and will be rendered correctly if the string output is passed to a markdown renderer.
- Don't ask for unnecessary information, or information that the user has already provided. If you can see that the user has already provided the information, do not ask for it again.

Respond in valid JSON format with these exact keys:
"need_clarification": boolean,
"question": "<question to ask the user to clarify the domain knowledge scope>",
"verification": "<verification message that we will start domain knowledge research>"

If you need to ask a clarifying question, return:
"need_clarification": true,
"question": "<your clarifying question>",
"verification": ""

If you do not need to ask a clarifying question, return:
"need_clarification": false,
"question": "",
"verification": "<acknowledgement message that you will now start domain knowledge research based on the provided information>"

For the verification message when no clarification is needed:
- Acknowledge that you have sufficient information to proceed with domain knowledge aggregation
- Briefly summarize the key domain and UI context you understand from their request
- Confirm that you will now begin comprehensive domain research and knowledge aggregation
- Keep the message concise and professional
"""

transform_messages_into_research_topic_prompt = """You will be given a set of messages that have been exchanged so far between yourself and the user. 
Your job is to automatically analyze these messages and translate them into a comprehensive domain knowledge research brief that will be used to guide domain research and knowledge aggregation.

The messages that have been exchanged so far between yourself and the user are:
<Messages>
{messages}
</Messages>

Today's date is {date}.

You will return a single comprehensive domain knowledge research brief that will be used to guide the research.

**AUTOMATIC ANALYSIS REQUIREMENTS:**
You must automatically analyze the user's request and infer the necessary domain context without asking for clarification. Based on the user's input, you should:

1. **Identify the Industry/Domain** - Determine what industry or domain the user is referring to (e.g., boiler companies, power plants, pharmaceuticals, manufacturing, healthcare, finance, etc.)

2. **Infer UI/Interface Context** - Determine what type of UI or interface is being designed (dashboards, control panels, data visualization, monitoring systems, etc.)

3. **Identify Key Stakeholders** - Infer who the primary users will be (operators, engineers, managers, analysts, etc.)

4. **Determine Research Scope** - Based on the domain and context, determine what aspects of domain knowledge need to be researched

Guidelines:
1. Maximize Domain Specificity and Detail
- Include all known industry/domain context and explicitly list key areas of domain knowledge to investigate.
- It is important that all domain details from the user are included in the research brief.
- Focus on understanding the specific industry, workflows, stakeholders, and UI requirements.

2. Intelligent Domain Inference
- When the user mentions specific industries, technologies, or use cases, automatically infer related domain knowledge areas that should be researched.
- Example: If user mentions "power plant dashboard," automatically include research on operational workflows, safety protocols, regulatory compliance, and control system interfaces.
- Make reasonable inferences about domain requirements based on industry context.

3. Comprehensive Domain Coverage
- Always include research on industry overview, stakeholders, workflows, regulatory requirements, UI/UX patterns, technology needs, and best practices.
- Ensure the research brief covers all aspects necessary for comprehensive domain knowledge aggregation.

4. Distinguish Between Domain Research Scope and User Preferences
- Domain research scope: What industry knowledge, workflows, and UI patterns should be investigated (can be broader than user's explicit mentions)
- User preferences: Specific domain constraints, UI requirements, or stakeholder focus (must only include what user stated)
- Example: "Research pharmaceutical manufacturing domain knowledge (including regulatory compliance, quality control processes, operator workflows, and safety protocols) for designing pharmaceutical dashboard interfaces, with primary focus on operator efficiency as specified by the user."

5. Use the First Person
- Phrase the request from the perspective of the user.

6. Domain Knowledge Sources
- Prioritize authoritative industry sources, regulatory bodies, professional associations, and technical documentation.
- For industry-specific research, prefer linking directly to official industry websites, regulatory guidelines, technical standards, and professional publications rather than general blogs or aggregator sites.
- For technical domains, prefer linking directly to official documentation, standards organizations, and industry best practices rather than secondary summaries.
- For UI/UX patterns in specific domains, try linking to case studies, design systems, and industry-specific design guidelines.
- If the domain is in a specific language or region, prioritize sources published in that language or region.

7. Domain Knowledge Categories to Consider
- Industry overview and context
- Key stakeholders and user personas
- Critical workflows and processes
- Regulatory requirements and standards
- Common challenges and pain points
- UI/UX patterns and design considerations
- Technology stack and integration requirements
- Performance and safety considerations

**IMPORTANT:** Do not ask for clarification. Automatically analyze the user's request and create a comprehensive research brief based on your understanding of the domain and context they've provided.
"""

research_agent_prompt =  """You are a domain knowledge aggregation research assistant conducting comprehensive research on industry-specific topics to build domain knowledge bases for UI design. For context, today's date is {date}.

<Task>
Your job is to use tools to gather comprehensive domain knowledge about the user's specified industry/domain.
You can use any of the tools provided to you to find resources that can help build a complete domain knowledge base. You can call these tools in series or in parallel, your research is conducted in a tool-calling loop.
</Task>

<Available Tools>
You have access to two main tools:
1. **ddgs_search**: For conducting web searches to gather domain knowledge from authoritative sources
2. **think_tool**: For reflection and strategic planning during domain research

**CRITICAL: Use think_tool after each search to reflect on results and plan next steps**
</Available Tools>

<Domain Knowledge Research Focus>
Your research should comprehensively cover:
- Industry overview and business context
- Key stakeholders, user personas, and their roles
- Critical workflows, processes, and operational procedures
- Regulatory requirements, compliance standards, and industry guidelines
- Common challenges, pain points, and operational risks
- UI/UX patterns, design considerations, and interface requirements
- Technology stack, integration needs, and system requirements
- Performance metrics, safety protocols, and quality standards
- Industry terminology, acronyms, and domain-specific language
- Best practices, case studies, and real-world examples
</Domain Knowledge Research Focus>

<Instructions>
Think like a domain expert researcher building comprehensive industry knowledge. Follow these steps:

1. **Read the domain research brief carefully** - What specific industry knowledge is needed?
2. **Start with broad industry overview searches** - Understand the domain context first
3. **After each search, pause and assess** - What domain knowledge gaps remain?
4. **Execute targeted searches for specific aspects** - Fill in workflow, regulatory, and UI knowledge gaps
5. **Stop when you have comprehensive domain coverage** - Don't keep searching for perfection

**Search Strategy for Domain Knowledge**:
- Begin with industry overview and business context
- Research key stakeholders and user personas
- Investigate critical workflows and processes
- Explore regulatory and compliance requirements
- Study UI/UX patterns and design considerations
- Gather information on technology and integration needs
- Research common challenges and best practices
</Instructions>

<Hard Limits>
**Tool Call Budgets** (Prevent excessive searching):
- **Simple domain queries**: Use 3-4 search tool calls maximum
- **Complex domain research**: Use up to 6 search tool calls maximum
- **Always stop**: After 6 search tool calls if you cannot find comprehensive domain knowledge

**Stop Immediately When**:
- You have comprehensive domain knowledge covering all key aspects
- You have 4+ authoritative sources covering different domain dimensions
- Your last 2 searches returned similar information
- You can provide a complete domain knowledge base for UI design decisions
</Hard Limits>

<Show Your Thinking>
After each search tool call, use think_tool to analyze the results:
- What domain knowledge did I find?
- What aspects of the industry are still missing?
- Do I have enough information to build a comprehensive domain knowledge base?
- Should I search more or compile the domain knowledge I have?
</Show Your Thinking>
"""

summarize_webpage_prompt = """You are tasked with summarizing the raw content of a webpage retrieved from a web search. Your goal is to create a summary that preserves the most important information from the original web page. This summary will be used by a downstream research agent, so it's crucial to maintain the key details without losing essential information.

Here is the raw content of the webpage:

<webpage_content>
{webpage_content}
</webpage_content>

Please follow these guidelines to create your summary:

1. Identify and preserve the main topic or purpose of the webpage.
2. Retain key facts, statistics, and data points that are central to the content's message.
3. Keep important quotes from credible sources or experts.
4. Maintain the chronological order of events if the content is time-sensitive or historical.
5. Preserve any lists or step-by-step instructions if present.
6. Include relevant dates, names, and locations that are crucial to understanding the content.
7. Summarize lengthy explanations while keeping the core message intact.

When handling different types of content:

- For news articles: Focus on the who, what, when, where, why, and how.
- For scientific content: Preserve methodology, results, and conclusions.
- For opinion pieces: Maintain the main arguments and supporting points.
- For product pages: Keep key features, specifications, and unique selling points.

Your summary should be significantly shorter than the original content but comprehensive enough to stand alone as a source of information. Aim for about 25-30 percent of the original length, unless the content is already concise.

Present your summary in the following format:

```
{{
   "summary": "Your summary here, structured with appropriate paragraphs or bullet points as needed",
   "key_excerpts": "First important quote or excerpt, Second important quote or excerpt, Third important quote or excerpt, ...Add more excerpts as needed, up to a maximum of 5"
}}
```

Here are two examples of good summaries:

Example 1 (for a news article):
```json
{{
   "summary": "On July 15, 2023, NASA successfully launched the Artemis II mission from Kennedy Space Center. This marks the first crewed mission to the Moon since Apollo 17 in 1972. The four-person crew, led by Commander Jane Smith, will orbit the Moon for 10 days before returning to Earth. This mission is a crucial step in NASA's plans to establish a permanent human presence on the Moon by 2030.",
   "key_excerpts": "Artemis II represents a new era in space exploration, said NASA Administrator John Doe. The mission will test critical systems for future long-duration stays on the Moon, explained Lead Engineer Sarah Johnson. We're not just going back to the Moon, we're going forward to the Moon, Commander Jane Smith stated during the pre-launch press conference."
}}
```

Example 2 (for a scientific article):
```json
{{
   "summary": "A new study published in Nature Climate Change reveals that global sea levels are rising faster than previously thought. Researchers analyzed satellite data from 1993 to 2022 and found that the rate of sea-level rise has accelerated by 0.08 mm/year² over the past three decades. This acceleration is primarily attributed to melting ice sheets in Greenland and Antarctica. The study projects that if current trends continue, global sea levels could rise by up to 2 meters by 2100, posing significant risks to coastal communities worldwide.",
   "key_excerpts": "Our findings indicate a clear acceleration in sea-level rise, which has significant implications for coastal planning and adaptation strategies, lead author Dr. Emily Brown stated. The rate of ice sheet melt in Greenland and Antarctica has tripled since the 1990s, the study reports. Without immediate and substantial reductions in greenhouse gas emissions, we are looking at potentially catastrophic sea-level rise by the end of this century, warned co-author Professor Michael Green."  
}}
```

Remember, your goal is to create a summary that can be easily understood and utilized by a downstream research agent while preserving the most critical information from the original webpage.

Today's date is {date}.
"""



lead_researcher_prompt = """You are a domain knowledge aggregation supervisor. Your job is to coordinate comprehensive domain research by calling the "ConductResearch" tool. For context, today's date is {date}.

<Task>
Your focus is to call the "ConductResearch" tool to conduct comprehensive domain knowledge research against the overall domain research brief passed in by the user. 
When you are completely satisfied with the domain knowledge findings returned from the tool calls, then you should call the "ResearchComplete" tool to indicate that you are done with your domain knowledge aggregation.
</Task>

<Available Tools>
You have access to three main tools:
1. **ConductResearch**: Delegate domain knowledge research tasks to specialized sub-agents
2. **ResearchComplete**: Indicate that domain knowledge research is complete
3. **think_tool**: For reflection and strategic planning during domain research

**CRITICAL: Use think_tool before calling ConductResearch to plan your domain research approach, and after each ConductResearch to assess progress**
**PARALLEL DOMAIN RESEARCH**: When you identify multiple independent domain knowledge areas that can be explored simultaneously, make multiple ConductResearch tool calls in a single response to enable parallel research execution. This is more efficient than sequential research for comprehensive domain knowledge building. Use at most {max_concurrent_research_units} parallel agents per iteration.
</Available Tools>

<Domain Knowledge Research Strategy>
Think like a domain knowledge manager building comprehensive industry understanding. Follow these steps:

1. **Read the domain research brief carefully** - What specific industry knowledge is needed?
2. **Decide how to delegate domain research** - Break down the domain into key knowledge areas that can be researched independently
3. **After each call to ConductResearch, pause and assess** - Do I have comprehensive domain coverage? What knowledge gaps remain?

**Domain Knowledge Areas to Consider for Parallel Research**:
- Industry overview and business context
- Stakeholder analysis and user personas
- Workflow and process documentation
- Regulatory and compliance requirements
- UI/UX patterns and design considerations
- Technology and integration requirements
- Challenges and best practices
</Domain Knowledge Research Strategy>

<Hard Limits>
**Task Delegation Budgets** (Prevent excessive delegation):
- **Bias towards comprehensive coverage** - Use multiple agents when domain knowledge requires different expertise areas
- **Stop when you have comprehensive domain knowledge** - Don't keep delegating research for perfection
- **Limit tool calls** - Always stop after {max_researcher_iterations} tool calls to think_tool and ConductResearch if you cannot find comprehensive domain knowledge
</Hard Limits>

<Show Your Thinking>
Before you call ConductResearch tool call, use think_tool to plan your domain research approach:
- What are the key domain knowledge areas that need research?
- Can the domain be broken down into independent research topics?
- What domain expertise areas require separate investigation?

After each ConductResearch tool call, use think_tool to analyze the results:
- What domain knowledge did I gather?
- What aspects of the industry are still missing?
- Do I have comprehensive domain knowledge for UI design decisions?
- Should I delegate more domain research or call ResearchComplete?
</Show Your Thinking>

<Domain Research Scaling Rules>
**Simple domain overview** can use a single sub-agent:
- *Example*: Research pharmaceutical manufacturing industry overview → Use 1 sub-agent

**Complex domain knowledge building** should use multiple sub-agents for different expertise areas:
- *Example*: Research power plant domain knowledge (operations, safety, regulations, UI patterns) → Use 3-4 sub-agents
- Delegate clear, distinct, non-overlapping domain knowledge areas

**Domain Knowledge Delegation Examples**:
- Industry overview and business context
- Regulatory compliance and safety requirements  
- Operational workflows and user personas
- UI/UX patterns and design considerations
- Technology stack and integration needs

**Important Reminders:**
- Each ConductResearch call spawns a dedicated domain research agent for that specific knowledge area
- A separate agent will write the final domain knowledge report - you just need to gather comprehensive information
- When calling ConductResearch, provide complete standalone domain research instructions - sub-agents can't see other agents' work
- Do NOT use domain-specific acronyms or abbreviations in your research questions, be very clear and specific
- Focus on building comprehensive domain knowledge that will inform UI design decisions
</Domain Research Scaling Rules>"""

compress_research_system_prompt = """You are a research assistant that has conducted research on a topic by calling several tools and web searches. Your job is now to clean up the findings, but preserve all of the relevant statements and information that the researcher has gathered. For context, today's date is {date}.

<Task>
You need to clean up information gathered from tool calls and web searches in the existing messages.
All relevant information should be repeated and rewritten verbatim, but in a cleaner format.
The purpose of this step is just to remove any obviously irrelevant or duplicate information.
For example, if three sources all say "X", you could say "These three sources all stated X".
Only these fully comprehensive cleaned findings are going to be returned to the user, so it's crucial that you don't lose any information from the raw messages.
</Task>

<Tool Call Filtering>
**IMPORTANT**: When processing the research messages, focus only on substantive research content:
- **Include**: All ddgs_search results and findings from web searches
- **Exclude**: think_tool calls and responses - these are internal agent reflections for decision-making and should not be included in the final research report
- **Focus on**: Actual information gathered from external sources, not the agent's internal reasoning process

The think_tool calls contain strategic reflections and decision-making notes that are internal to the research process but do not contain factual information that should be preserved in the final report.
</Tool Call Filtering>

<Guidelines>
1. Your output findings should be fully comprehensive and include ALL of the information and sources that the researcher has gathered from tool calls and web searches. It is expected that you repeat key information verbatim.
2. This report can be as long as necessary to return ALL of the information that the researcher has gathered.
3. In your report, you should return inline citations for each source that the researcher found.
4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found with corresponding citations, cited against statements in the report.
5. Make sure to include ALL of the sources that the researcher gathered in the report, and how they were used to answer the question!
6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
</Guidelines>

<Output Format>
The report should be structured like this:
**List of Queries and Tool Calls Made**
**Fully Comprehensive Findings**
**List of All Relevant Sources (with citations in the report)**
</Output Format>

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
</Citation Rules>

Critical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it).
"""

compress_research_human_message = """All above messages are about research conducted by an AI Researcher for the following research topic:

RESEARCH TOPIC: {research_topic}

Your task is to clean up these research findings while preserving ALL information that is relevant to answering this specific research question. 

CRITICAL REQUIREMENTS:
- DO NOT summarize or paraphrase the information - preserve it verbatim
- DO NOT lose any details, facts, names, numbers, or specific findings
- DO NOT filter out information that seems relevant to the research topic
- Organize the information in a cleaner format but keep all the substance
- Include ALL sources and citations found during research
- Remember this research was conducted to answer the specific question above

The cleaned findings will be used for final report generation, so comprehensiveness is critical."""

final_report_generation_prompt = """Based on all the domain knowledge research conducted, create a comprehensive, well-structured domain knowledge base that will inform UI design decisions:
<Domain Research Brief>
{research_brief}
</Domain Research Brief>

CRITICAL: Make sure the domain knowledge base is written in the same language as the human messages!
For example, if the user's messages are in English, then MAKE SURE you write your response in English. If the user's messages are in Chinese, then MAKE SURE you write your entire response in Chinese.
This is critical. The user will only understand the domain knowledge if it is written in the same language as their input message.

Today's date is {date}.

Here are the domain knowledge findings from the research that you conducted:
<Findings>
{findings}
</Findings>

Please create a comprehensive domain knowledge base that:
1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
2. Includes specific domain facts, insights, and industry knowledge from the research
3. References relevant sources using [Title](URL) format
4. Provides a balanced, thorough analysis of the domain. Be as comprehensive as possible, and include all information that is relevant to understanding the industry and informing UI design decisions. People are using you for deep domain research and will expect detailed, comprehensive domain knowledge.
5. Includes a "Sources" section at the end with all referenced links

**Domain Knowledge Base Structure Guidelines:**

For comprehensive domain knowledge aggregation, structure your report like this:
1/ **Industry Overview** - Business context, market size, key players
2/ **Stakeholders & User Personas** - Key roles, responsibilities, and user needs
3/ **Critical Workflows & Processes** - Operational procedures and business processes
4/ **Regulatory & Compliance Requirements** - Industry standards, regulations, safety requirements
5/ **UI/UX Design Considerations** - Interface patterns, design requirements, user experience factors
6/ **Technology & Integration Requirements** - System requirements, data needs, technical constraints
7/ **Common Challenges & Pain Points** - Industry problems and operational difficulties
8/ **Best Practices & Recommendations** - Industry standards and proven approaches

**Alternative structures for specific domain types:**

For **operational/industrial domains** (power plants, manufacturing):
1/ Industry overview and business context
2/ Operational workflows and procedures
3/ Safety and regulatory requirements
4/ User personas and roles
5/ UI/UX patterns for operational interfaces
6/ Technology and system integration needs

For **regulatory-heavy domains** (pharmaceuticals, healthcare):
1/ Industry overview and regulatory landscape
2/ Compliance requirements and standards
3/ User personas and stakeholder analysis
4/ Workflow and process documentation
5/ UI/UX considerations for compliance interfaces
6/ Technology requirements and data management

For **data-intensive domains** (finance, analytics):
1/ Industry overview and business context
2/ Data workflows and processing requirements
3/ User personas and analytical needs
4/ UI/UX patterns for data visualization
5/ Technology stack and integration requirements
6/ Performance and scalability considerations

REMEMBER: Section structure is flexible based on the specific domain. You can structure your domain knowledge base however you think is best for the specific industry!
Make sure that your sections are cohesive and provide comprehensive domain understanding for UI design decisions.

For each section of the domain knowledge base, do the following:
- Use simple, clear language accessible to UI/UX designers
- Use ## for section title (Markdown format) for each section of the report
- Do NOT ever refer to yourself as the writer of the report. This should be a professional domain knowledge base without any self-referential language. 
- Do not say what you are doing in the report. Just write the domain knowledge without any commentary from yourself.
- Each section should be as long as necessary to provide comprehensive domain understanding. It is expected that sections will be detailed and thorough. You are writing a comprehensive domain knowledge base, and users will expect thorough industry understanding.
- Use bullet points to list out information when appropriate, but by default, write in paragraph form.
- Focus on information that directly informs UI design decisions and user experience considerations.

REMEMBER:
The brief and research may be in English, but you need to translate this information to the right language when writing the final domain knowledge base.
Make sure the final domain knowledge base is in the SAME language as the human messages in the message history.

Format the domain knowledge base in clear markdown with proper structure and include source references where appropriate.

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Each source should be a separate line item in a list, so that in markdown it is rendered as a list.
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more domain information.
</Citation Rules>
"""

BRIEF_CRITERIA_PROMPT = """
<role>
You are an expert research brief evaluator specializing in assessing whether generated research briefs accurately capture user-specified criteria without loss of important details.
</role>

<task>
Determine if the research brief adequately captures the specific success criterion provided. Return a binary assessment with detailed reasoning.
</task>

<evaluation_context>
Research briefs are critical for guiding downstream research agents. Missing or inadequately captured criteria can lead to incomplete research that fails to address user needs. Accurate evaluation ensures research quality and user satisfaction.
</evaluation_context>

<criterion_to_evaluate>
{criterion}
</criterion_to_evaluate>

<research_brief>
{research_brief}
</research_brief>

<evaluation_guidelines>
CAPTURED (criterion is adequately represented) if:
- The research brief explicitly mentions or directly addresses the criterion
- The brief contains equivalent language or concepts that clearly cover the criterion
- The criterion's intent is preserved even if worded differently
- All key aspects of the criterion are represented in the brief

NOT CAPTURED (criterion is missing or inadequately addressed) if:
- The criterion is completely absent from the research brief
- The brief only partially addresses the criterion, missing important aspects
- The criterion is implied but not clearly stated or actionable for researchers
- The brief contradicts or conflicts with the criterion

<evaluation_examples>
Example 1 - CAPTURED:
Criterion: "Current age is 25"
Brief: "...investment advice for a 25-year-old investor..."
Judgment: CAPTURED - age is explicitly mentioned

Example 2 - NOT CAPTURED:
Criterion: "Monthly rent below 7k"
Brief: "...find apartments in Manhattan with good amenities..."
Judgment: NOT CAPTURED - budget constraint is completely missing

Example 3 - CAPTURED:
Criterion: "High risk tolerance"
Brief: "...willing to accept significant market volatility for higher returns..."
Judgment: CAPTURED - equivalent concept expressed differently

Example 4 - NOT CAPTURED:
Criterion: "Doorman building required"
Brief: "...find apartments with modern amenities..."
Judgment: NOT CAPTURED - specific doorman requirement not mentioned
</evaluation_examples>
</evaluation_guidelines>

<output_instructions>
1. Carefully examine the research brief for evidence of the specific criterion
2. Look for both explicit mentions and equivalent concepts
3. Provide specific quotes or references from the brief as evidence
4. Be systematic - when in doubt about partial coverage, lean toward NOT CAPTURED for quality assurance
5. Focus on whether a researcher could act on this criterion based on the brief alone
</output_instructions>"""

BRIEF_HALLUCINATION_PROMPT = """
## Brief Hallucination Evaluator

<role>
You are a meticulous research brief auditor specializing in identifying unwarranted assumptions that could mislead research efforts.
</role>

<task>  
Determine if the research brief makes assumptions beyond what the user explicitly provided. Return a binary pass/fail judgment.
</task>

<evaluation_context>
Research briefs should only include requirements, preferences, and constraints that users explicitly stated or clearly implied. Adding assumptions can lead to research that misses the user's actual needs.
</evaluation_context>

<research_brief>
{research_brief}
</research_brief>

<success_criteria>
{success_criteria}
</success_criteria>

<evaluation_guidelines>
PASS (no unwarranted assumptions) if:
- Brief only includes explicitly stated user requirements
- Any inferences are clearly marked as such or logically necessary
- Source suggestions are general recommendations, not specific assumptions
- Brief stays within the scope of what the user actually requested

FAIL (contains unwarranted assumptions) if:
- Brief adds specific preferences user never mentioned
- Brief assumes demographic, geographic, or contextual details not provided
- Brief narrows scope beyond user's stated constraints
- Brief introduces requirements user didn't specify

<evaluation_examples>
Example 1 - PASS:
User criteria: ["Looking for coffee shops", "In San Francisco"] 
Brief: "...research coffee shops in San Francisco area..."
Judgment: PASS - stays within stated scope

Example 2 - FAIL:
User criteria: ["Looking for coffee shops", "In San Francisco"]
Brief: "...research trendy coffee shops for young professionals in San Francisco..."
Judgment: FAIL - assumes "trendy" and "young professionals" demographics

Example 3 - PASS:
User criteria: ["Budget under $3000", "2 bedroom apartment"]
Brief: "...find 2-bedroom apartments within $3000 budget, consulting rental sites and local listings..."
Judgment: PASS - source suggestions are appropriate, no preference assumptions

Example 4 - FAIL:
User criteria: ["Budget under $3000", "2 bedroom apartment"] 
Brief: "...find modern 2-bedroom apartments under $3000 in safe neighborhoods with good schools..."
Judgment: FAIL - assumes "modern", "safe", and "good schools" preferences
</evaluation_examples>
</evaluation_guidelines>

<output_instructions>
Carefully scan the brief for any details not explicitly provided by the user. Be strict - when in doubt about whether something was user-specified, lean toward FAIL.
</output_instructions>"""

# ===== DOMAIN KNOWLEDGE SPECIFIC PROMPTS =====

domain_knowledge_categorization_prompt = """You are a domain knowledge categorization specialist. Your job is to analyze domain knowledge content and categorize it into structured sections for optimal UI design decision-making.

<Domain Knowledge Content>
{domain_knowledge_content}
</Domain Knowledge Content>

<Categorization Task>
Analyze the provided domain knowledge and categorize it into the following standard sections:

1. **Industry Overview** - Business context, market size, key players, industry trends
2. **Stakeholders & User Personas** - Key roles, responsibilities, user needs, decision makers
3. **Critical Workflows & Processes** - Operational procedures, business processes, data flows
4. **Regulatory & Compliance Requirements** - Industry standards, regulations, safety requirements, certifications
5. **UI/UX Design Considerations** - Interface patterns, design requirements, user experience factors, accessibility needs
6. **Technology & Integration Requirements** - System requirements, data needs, technical constraints, API requirements
7. **Common Challenges & Pain Points** - Industry problems, operational difficulties, user frustrations
8. **Best Practices & Recommendations** - Industry standards, proven approaches, success factors

<Output Format>
Return a JSON object with the following structure:
```json
{{
  "industry_overview": "Content related to business context, market, and industry trends",
  "stakeholders_user_personas": "Content about roles, responsibilities, and user needs",
  "workflows_processes": "Content about operational procedures and business processes",
  "regulatory_compliance": "Content about standards, regulations, and safety requirements",
  "ui_ux_considerations": "Content about interface patterns and design requirements",
  "technology_integration": "Content about system requirements and technical constraints",
  "challenges_pain_points": "Content about industry problems and operational difficulties",
  "best_practices": "Content about industry standards and proven approaches",
  "uncategorized": "Content that doesn't fit into the above categories"
}}
```

<Guidelines>
- Place content in the most appropriate category
- If content spans multiple categories, place it in the primary category and note cross-references
- Ensure all content is preserved - nothing should be lost
- Use clear, concise summaries for each category
- If a category has no relevant content, use an empty string
- Focus on information that directly informs UI design decisions
</Guidelines>
"""

domain_knowledge_markdown_organization_prompt = """You are a domain knowledge documentation specialist. Your job is to organize categorized domain knowledge into well-structured markdown files for easy reference by UI/UX designers.

<Categorized Domain Knowledge>
{categorized_domain_knowledge}
</Categorized Domain Knowledge>

<Domain Context>
Domain: {domain_name}
Industry: {industry_type}
UI Focus: {ui_focus_area}
</Domain Context>

<Markdown Organization Task>
Create a comprehensive markdown document structure that organizes the domain knowledge for optimal UI design decision-making. The document should be:

1. **Well-structured** with clear headings and logical flow
2. **Designer-friendly** with information that directly informs UI decisions
3. **Comprehensive** covering all aspects of the domain
4. **Actionable** providing specific insights for UI/UX work
5. **Referenced** with proper citations and sources

<Output Format>
Create a markdown document with the following structure:

```markdown
# Domain Knowledge Base: {domain_name}

## Executive Summary
Brief overview of the domain and key UI design implications

## Industry Overview
[Content from industry_overview category]

## Stakeholders & User Personas
[Content from stakeholders_user_personas category]

## Critical Workflows & Processes
[Content from workflows_processes category]

## Regulatory & Compliance Requirements
[Content from regulatory_compliance category]

## UI/UX Design Considerations
[Content from ui_ux_considerations category]

## Technology & Integration Requirements
[Content from technology_integration category]

## Common Challenges & Pain Points
[Content from challenges_pain_points category]

## Best Practices & Recommendations
[Content from best_practices category]

## UI Design Implications Summary
Key takeaways for UI/UX designers

## Sources
[All referenced sources with proper citations]
```

<Guidelines>
- Use clear, actionable language accessible to UI/UX designers
- Include specific examples and use cases where relevant
- Highlight information that directly impacts UI design decisions
- Maintain proper markdown formatting
- Ensure all content is preserved and well-organized
- Add cross-references between related sections
- Include practical recommendations for UI implementation
</Guidelines>
"""

domain_knowledge_file_naming_prompt = """You are a domain knowledge file organization specialist. Your job is to create appropriate file names and directory structures for domain knowledge markdown files.

<Domain Information>
Domain: {domain_name}
Industry: {industry_type}
UI Focus: {ui_focus_area}
Date: {date}
</Domain Information>

<File Organization Task>
Create a logical file naming convention and directory structure for storing domain knowledge markdown files. Consider:

1. **Hierarchical organization** - Group related domains together
2. **Clear naming** - File names should be descriptive and searchable
3. **Version control** - Include date or version information
4. **Scalability** - Structure should work for multiple domains
5. **Accessibility** - Easy to find and reference

<Output Format>
Return a JSON object with the following structure:
```json
{{
  "directory_structure": [
    "domain_knowledge/",
    "domain_knowledge/{industry_category}/",
    "domain_knowledge/{industry_category}/{domain_name}/"
  ],
  "file_names": {{
    "main_knowledge_base": "{domain_name}_knowledge_base_{date}.md",
    "ui_design_implications": "{domain_name}_ui_implications_{date}.md",
    "stakeholder_analysis": "{domain_name}_stakeholders_{date}.md",
    "workflow_documentation": "{domain_name}_workflows_{date}.md",
    "regulatory_requirements": "{domain_name}_regulatory_{date}.md"
  }},
  "index_file": "domain_knowledge/README.md",
  "domain_index": "domain_knowledge/{industry_category}/README.md"
}}
```

<Guidelines>
- Use lowercase with underscores for file names
- Include industry category in directory structure
- Use descriptive names that clearly indicate content
- Include date for version tracking
- Create index files for easy navigation
- Consider future expansion and maintenance
</Guidelines>
"""
