"""
Prompt templates for dynamic content generation.

Templates with variable substitution for each agent role.
"""

import sys
from pathlib import Path
from string import Template

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from .system_prompts import AGENT_CONTEXT_PREP, QUALITY_GATE
except ImportError:
    from system_prompts import AGENT_CONTEXT_PREP, QUALITY_GATE


# Researcher Agent Templates
RESEARCHER_PROMPT_TEMPLATE = Template("""
Analyze the existing blog knowledge base and create a comprehensive research brief for a new blog post on this topic:

TOPIC: $topic

$context_prep

EXISTING CONTEXT:
$relevant_context

GENERATION SPECIFICATIONS:
- Style: $style
- Target Length: $word_count_range words
- Target Audience: $audience
- Key Requirements: $requirements

Create a research brief that includes:
1. Key themes and concepts from existing content
2. Relevant facts and findings to incorporate
3. Related topics covered in the knowledge base
4. Content gaps and opportunities
5. Recommended focus areas for the new post
6. Connection opportunities with existing posts

Structure your response with clear section headers.
$quality_gate
""")

# Outliner Agent Templates
OUTLINER_PROMPT_TEMPLATE = Template("""
Create a detailed, SEO-optimized outline for a blog post based on the research brief and specifications.

TOPIC: $topic

RESEARCH BRIEF:
$research_brief

GENERATION SPECIFICATIONS:
- Style: $style
- Target Length: $word_count_range words
- Categories: $categories
- Keywords: $keywords

Create an outline that includes:
1. Compelling H1 title with primary keyword
2. 3-7 H2 main sections with descriptive headings
3. Subsections under each H2 (use H3s where appropriate)
4. Key points to cover in each section
5. Word count targets per section
6. SEO optimization notes (keyword placement, internal linking)
7. Introduction and conclusion objectives

Format the outline in markdown with clear section hierarchies.
$context_prep
$quality_gate

Ensure the outline will produce content of $word_count_range words total.
""")

# Writer Agent Templates
WRITER_PROMPT_TEMPLATE = Template("""
Write a complete blog post following the provided outline and incorporating insights from the research brief.

OUTLINE TO FOLLOW:
$outline

RESEARCH BRIEF & CONTEXT:
$research_context

WRITING SPECIFICATIONS:
- Style: $style
- Total Target Length: $word_count_range words
- Tone: $tone
- Keywords to incorporate naturally: $keywords
- Categories: $categories

Writing requirements:
- Start with an engaging introduction (150-250 words)
- Follow the outline structure exactly
- Incorporate insights from existing posts naturally
- End with a compelling conclusion with call-to-action
- Use clear, scannable formatting (headings, lists, bold emphasis)
- Maintain consistent technical accuracy
- Include practical examples and actionable advice
- Write in engaging, professional voice

Output only the complete blog post content in markdown format.
$context_prep
$quality_gate
""")

# Editor Agent Templates
EDITOR_PROMPT_TEMPLATE = Template("""
Edit and polish the following blog post draft to maximize clarity, engagement, and professional quality.

ORIGINAL DRAFT:
$draft_content

EDITING REQUIREMENTS:
- Improve clarity and precision in technical explanations
- Enhance readability while maintaining technical accuracy
- Strengthen transitions between sections
- Verify consistent voice and tone throughout
- Polish language for grammatical precision and elegance
- Ensure proper markdown formatting
- Optimize scannability with headings, lists, and emphasis
- Remove redundancy and wordiness
- Strengthen weak arguments with clearer explanations

Do not change the core meaning or facts, but improve the presentation significantly.
Maintain the target length of $word_count_range words.

Output the fully edited version ready for publication.
$context_prep
$quality_gate
""")

# SEO Optimizer Templates
SEO_OPTIMIZER_PROMPT_TEMPLATE = Template("""
Analyze and optimize the following blog post for search engine visibility and user engagement.

CONTENT TO OPTIMIZE:
$edited_content

OPTIMIZATION SPECIFICATIONS:
- Target Keywords: $keywords
- Content Categories: $categories
- Target Length: $word_count_range words

SEO ANALYSIS & OPTIMIZATION:
1. Title Optimization (30-60 characters): Suggest improved title with primary keyword
2. Meta Description (150-160 characters): Create compelling summary
3. Heading Structure: Review H1-H3 hierarchy and keyword distribution
4. Keyword Usage: Assess natural keyword density ($keyword_density_target)
5. Internal Linking: Suggest 3-5 links to related posts from knowledge base
6. Content Structure: Ensure proper depth and coverage
7. Technical SEO: Verify mobile-friendly formatting and readability

Provide specific recommendations and the optimized metadata.
$context_prep
$quality_gate
""")

# Validation Templates
RETRIEVER_PROMPT_TEMPLATE = Template("""
Based on the provided context from the knowledge base, create a concise summary and extract relevant excerpts for the new blog post topic.

TOPIC: $topic

RETRIEVED CONTEXT:
$context

INSTRUCTIONS:
1. Create a concise summary (100-200 words) that captures the essence of relevant existing content and its relationship to the topic
2. Extract $excerpt_limit of the most relevant excerpts that would inform the new post
3. Highlight key themes, insights, and connections from existing posts
4. Focus on substantive, actionable content that adds value to the new post

Format your response as:
SUMMARY: [Your concise synthesis here]

RELEVANT EXCERPTS:
- [Quote or paraphrase from most relevant section]
- [Next most relevant excerpt]
- [Continue as needed]

Ensure excerpts are directly useful for creating original, valuable new content.
""")

COMPOSER_PROMPT_TEMPLATE = Template("""
Create an initial blog post draft based on the retriever's context synthesis and the generation specifications.

TOPIC: $topic

RETRIEVER CONTEXT:
Summary: $summary

Relevant Excerpts:
$excerpts

GENERATION SPECIFICATIONS:
- Style: $style
- Target Length: $length words ($min_words - $max_words range)
- Tone: $tone
- Categories: $categories
- Tags: $tags

STRUCTURE REQUIREMENTS:
1. H1 title with primary keywords (use # )
2. Engaging introduction that hooks the reader
3. 3-5 main content sections with H2 headings (use ## )
4. Conclusion with key takeaways and next steps
5. Proper markdown formatting throughout

CONTENT GUIDELINES:
- Incorporate insights from the retriever context naturally
- Write in authoritative, engaging voice
- Balance technical depth with accessibility
- Include practical examples and actionable advice
- Ensure logical flow and smooth transitions
- Target the specified word count range

IMPORTANT: DO NOT include any YAML frontmatter, metadata headers, or --- delimiters. Start directly with the H1 title and output only the markdown body content.
""")

REFINER_PROMPT_TEMPLATE = Template("""
Review and refine the blog post draft to improve structure, clarity, and engagement.

ORIGINAL DRAFT:
$draft_content

REFINEMENT TASKS:
1. Enhance structure and logical flow
2. Improve readability and engagement
3. Expand sections that lack sufficient detail
4. Strengthen weak arguments with better explanations
5. Eliminate redundancy and improve coherence
6. Polish language for professional quality
7. Verify technical accuracy and terminology
8. Optimize for the target audience understanding

TARGET LENGTH: $length words (maintain $min_words - $max_words range)

SPECIFICATIONS TO MAINTAIN:
- Style: $style
- Tone: $tone
- Categories: $categories
- Tags: $tags

IMPORTANT: DO NOT include any YAML frontmatter or metadata headers. Output only the refined markdown body content starting with the H1 title.

Output the refined version with clear improvements while preserving the core content and structure.
""")

EVALUATOR_PROMPT_TEMPLATE = Template("""
Evaluate the blog post draft against quality standards and determine if it meets publication criteria.

CONTENT TO EVALUATE:
$draft_content

EVALUATION CRITERIA:
- ✅ Structure: Clear introduction, body sections, and conclusion
- ✅ Word count: Within $min_words - $max_words range (current: $current_words)
- ✅ Markdown formatting: Proper headings, lists, links, code blocks
- ✅ Coherence: Logical flow, smooth transitions, consistent tone
- ✅ Factual accuracy: Technically correct claims and explanations
- ✅ Originality: Adds clear value beyond existing content
- ✅ Engagement: Compelling, readable, actionable content

REQUIRED FOR APPROVAL:
- Must pass ALL structural checks
- Must meet word count requirements
- Must use correct markdown throughout
- Must demonstrate sufficient quality in coherence, accuracy, and originality

If APPROVED: Output only "APPROVED" followed by a brief justification.

If REJECTED: Output "REJECTED" followed by specific, actionable feedback:
- List each failing criterion
- Provide exact locations of problems
- Suggest specific improvements
- Prioritize fixes by impact and effort
""")

INGESTOR_PROMPT_TEMPLATE = Template("""
The blog post has been approved for publication. Prepare the final output files and ingestion metadata.

APPROVED CONTENT:
$final_content

INGESTION REQUIREMENTS:
1. Generate slug from title for URL-safe filename
2. Create ./content/posts/{slug}.md file
3. Ensure proper frontmatter is included
4. Prepare content chunks for vector storage
5. Generate embeddings for searchability
6. Update knowledge base with new content

VALIDATION CHECKS:
- Confirm file was saved successfully
- Verify frontmatter completeness
- Ensure content is chunked appropriately
- Confirm embeddings were generated
- Validate retrievability of new content

Output confirmation when ingestion is complete and provide the final file path.
""")

VALIDATION_FEEDBACK_TEMPLATE = Template("""
Provide specific feedback on the following content validation issues:

VALIDATION RESULTS:
$validation_results

CONTENT DRAFT:
$draft_content

GUIDANCE NEEDED:
- Address critical errors that prevent publication
- Suggest fixes for warnings to improve quality
- Provide specific examples for improvement
- Prioritize changes by impact and urgency

Output actionable feedback with prioritized recommendations.
""")


# Helper functions for template rendering
def render_researcher_prompt(topic, relevant_context, spec):
    """Render researcher prompt with variables."""
    return RESEARCHER_PROMPT_TEMPLATE.substitute(
        topic=topic,
        context_prep=AGENT_CONTEXT_PREP,
        relevant_context=relevant_context,
        style=spec.get('style', 'technical'),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        audience=spec.get('audience', 'technical professionals'),
        requirements=spec.get('requirements', 'Comprehensive technical coverage'),
        quality_gate=QUALITY_GATE
    )


def render_outliner_prompt(topic, research_brief, spec):
    """Render outliner prompt with variables."""
    return OUTLINER_PROMPT_TEMPLATE.substitute(
        topic=topic,
        research_brief=research_brief,
        style=spec.get('style', 'technical'),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        categories=', '.join(spec.get('categories', [])),
        keywords=', '.join(spec.get('keywords', [])),
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE,
        total_word_target=spec.get('word_target', 1500)
    )


def render_writer_prompt(outline, research_context, spec):
    """Render writer prompt with variables."""
    return WRITER_PROMPT_TEMPLATE.substitute(
        outline=outline,
        research_context=research_context,
        style=spec.get('style', 'technical'),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        tone=spec.get('tone', 'informative'),
        keywords=', '.join(spec.get('keywords', [])),
        categories=', '.join(spec.get('categories', [])),
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE
    )


def render_editor_prompt(draft_content, spec):
    """Render editor prompt with variables."""
    return EDITOR_PROMPT_TEMPLATE.substitute(
        draft_content=draft_content,
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE
    )


def render_seo_optimizer_prompt(edited_content, spec):
    """Render SEO optimizer prompt with variables."""
    return SEO_OPTIMIZER_PROMPT_TEMPLATE.substitute(
        edited_content=edited_content,
        keywords=', '.join(spec.get('keywords', [])),
        categories=', '.join(spec.get('categories', [])),
        word_count_range=f"{spec.get('min_words', 800)}-{spec.get('max_words', 2000)}",
        keyword_density_target=f"{spec.get('keyword_density', 0.02) * 100:.1f}%",
        context_prep=AGENT_CONTEXT_PREP,
        quality_gate=QUALITY_GATE
    )
