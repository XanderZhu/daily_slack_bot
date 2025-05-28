from settings import settings
from .base import BaseAgent
from autogen import ConversableAgent, GroupChat, GroupChatManager
from pydantic import BaseModel, Field


class Choice(BaseModel):
    title: str
    question: str
    options: list[str]
    answer: str
    is_multiple: bool


class TextQuestion(BaseModel):
    title: str
    question: str


class Theory(BaseModel):
    title: str = Field(description="The name of the card")
    content: str = Field(description="The content/body of the theory")


class AutogenCardGeneratorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("feature_name", "unified_content_generation_agent")
        super().__init__(*args, **kwargs)
        self.max_rounds = 5

    async def invoke(
        self, step, subtopic, created_cards, learning_path, user_id, locale
    ):
        llm_config = {
            "model": "gemini/gemini-2.5-flash-preview-04-17",
            "api_key": settings.litellm.api_key,
            "base_url": settings.litellm.base_url,
            "stream": False,
            "metadata": {
                "generation_name": self.feature_name,  # Custom generation name
                "trace_name": self.feature_name,  # Custom trace name
                "trace_user_id": str(user_id),  # User ID for tracing
                "tags": ["edvancium", self.model, self.feature_name],  # Custom tags
                # Additional optional parameters:
                # "trace_id": "custom-trace-id",
                # "trace_version": "1.0",
                # "trace_release": "release-identifier",
                # "trace_metadata": {"key": "value"},
            },
        }
        writer_llm_config = {
            "model": "gemini/gemini-2.5-flash-preview-04-17",
            "reasoning_effort": "high",
            "api_key": settings.litellm.api_key,
            "base_url": settings.litellm.base_url,
            "stream": False,
            "metadata": {
                "trace_name": "content_writer_trace",
                "trace_user_id": str(user_id),
                "tags": ["edvancium", "writer", self.feature_name],
            },
        }
        reviewer_llm_config = {
            "model": "gemini/gemini-2.5-flash-preview-04-17",
            "reasoning_effort": "high",
            "api_key": settings.litellm.api_key,
            "base_url": settings.litellm.base_url,
            "stream": False,
            "metadata": {
                "trace_name": "content_reviewer_trace",
                "trace_user_id": str(user_id),
                "tags": ["edvancium", "reviewer", self.feature_name],
            },
        }
        if step.step_type == "image":
            return None

        if step.step_type == "theory":
            # Load prompts using prompt service
            word_count = "40-50" if not created_cards else "70-80"

            # Get theory writer prompt
            theory_writer_prompt = self.prompt_service.get_prompt(
                "prompts/team/card_generators/v1.0.0/theory_writer"
            ).compile(
                subtopic=subtopic,
                word_count=word_count,
                step=step,
                created_cards=created_cards,
            )

            # Get theory reviewer prompt
            theory_reviewer_prompt = self.prompt_service.get_prompt(
                "prompts/team/card_generators/v1.0.0/theory_reviewer"
            ).compile(
                subtopic=subtopic,
                word_count=word_count,
                learning_path=learning_path,
                step=step,
                created_cards=created_cards,
            )

            content_writer = ConversableAgent(
                name="theory_writer_agent",
                human_input_mode="NEVER",
                is_termination_msg=lambda x: "DONE!"
                in (x.get("content", "") or "").upper(),
                llm_config=writer_llm_config,
                system_message=theory_writer_prompt,
                description=f"""Creates concise educational topic cards of {word_count} words based on given content plan.""",
            )

            content_reviewer = ConversableAgent(
                name="theory_reviewer_agent",
                is_termination_msg=lambda x: "DONE!"
                in (x.get("content", "") or "").upper(),
                human_input_mode="NEVER",
                llm_config=reviewer_llm_config,
                system_message=theory_reviewer_prompt,
                description=f"""Reviews educational topic cards for length {word_count} words, coherence, and accuracy.""",
            )
        elif step.step_type == "quiz":
            # Load prompts using prompt service
            quiz_writer_prompt = self.prompt_service.get_prompt(
                "prompts/team/card_generators/v1.0.0/quiz_writer"
            ).compile(subtopic=subtopic, step=step, created_cards=created_cards)

            quiz_reviewer_prompt = self.prompt_service.get_prompt(
                "prompts/team/card_generators/v1.0.0/quiz_reviewer"
            ).compile(subtopic=subtopic, step=step, created_cards=created_cards)

            content_writer = ConversableAgent(
                name="quiz_writer_agent",
                human_input_mode="NEVER",
                is_termination_msg=lambda x: "DONE!"
                in (x.get("content", "") or "").upper(),
                llm_config=writer_llm_config,
                system_message=quiz_writer_prompt,
                description="Creates quiz questions with 4 choice options based on given task",
            )

            content_reviewer = ConversableAgent(
                name="quiz_reviewer_agent",
                is_termination_msg=lambda x: "DONE!"
                in (x.get("content", "") or "").upper(),
                human_input_mode="NEVER",
                llm_config=reviewer_llm_config,
                system_message=quiz_reviewer_prompt,
                description="Reviews quiz questions for clarity, format, and effectiveness.",
            )
        elif step.step_type == "text_question":
            # Load prompts using prompt service
            text_question_writer_prompt = self.prompt_service.get_prompt(
                "prompts/team/card_generators/v1.0.0/text_question_writer"
            ).compile(subtopic=subtopic, step=step, created_cards=created_cards)

            text_question_reviewer_prompt = self.prompt_service.get_prompt(
                "prompts/team/card_generators/v1.0.0/text_question_reviewer"
            ).compile(subtopic=subtopic, step=step, created_cards=created_cards)

            content_writer = ConversableAgent(
                name="text_question_writer_agent",
                human_input_mode="NEVER",
                is_termination_msg=lambda x: "DONE!"
                in (x.get("content", "") or "").upper(),
                llm_config=llm_config,
                system_message=text_question_writer_prompt,
                description="Creates text questions based on given task",
            )

            content_reviewer = ConversableAgent(
                name="text_question_reviewer_agent",
                is_termination_msg=lambda x: "DONE!"
                in (x.get("content", "") or "").upper(),
                human_input_mode="NEVER",
                llm_config=llm_config,
                system_message=text_question_reviewer_prompt,
                description="Reviews text questions for clarity, format, and effectiveness.",
            )
        else:
            # For any other step type not explicitly handled, return None
            return None

        # Define parser templates for different content types using prompt service
        parser_type_map = {
            "theory": "theory_parser",
            "choice": "choice_parser",
            "quiz": "choice_parser",  # Use the same parser for quiz and choice
            "text_question": "text_question_parser",
        }

        # Get the appropriate parser prompt for this step type
        parser_key = "choice" if step.step_type == "quiz" else step.step_type
        parser_prompt_name = parser_type_map.get(parser_key)

        if parser_prompt_name is None:
            raise ValueError(f"Unsupported step_type: {step.step_type}")

        parser_prompt = self.prompt_service.get_prompt(
            f"prompts/team/card_generators/v1.0.0/{parser_prompt_name}"
        ).compile(locale=locale)

        # Map step types to Pydantic models
        model_map = {
            "theory": Theory,
            "choice": Choice,
            "quiz": Choice,  # Map quiz to Choice model as well for compatibility
            "text_question": TextQuestion,
        }
        response_model = model_map.get(step.step_type)
        if response_model is None:
            raise ValueError(f"No model mapping for step_type: {step.step_type}")

        # Parser LLM config with structured output
        parser_llm_config = {
            "model": llm_config["model"],
            "reasoning_effort": "high",
            "api_key": llm_config["api_key"],
            "base_url": llm_config["base_url"],
            "stream": False,
            "metadata": {
                "trace_name": "content_parser_trace",
                "trace_user_id": str(user_id),
                "tags": ["edvancium", "parser", self.feature_name],
            },
            "response_format": response_model,
        }

        # Create a parser agent to parse the approved content
        content_parser = ConversableAgent(
            name="content_parser_agent",
            human_input_mode="NEVER",
            is_termination_msg=lambda msg: msg.get("content", "")
            .strip()
            .startswith("{"),
            llm_config=parser_llm_config,
            system_message=parser_prompt,
            description="Parses approved content into structured data models.",
        )

        def autogen_selector(last_speaker: ConversableAgent, groupchat: GroupChat):
            """
            Routes turns as:
              – first turn → writer
              – writer   → reviewer
              – reviewer → parser (if "DONE!") or back to writer
              – parser   → parser (one‐and‐done)
            """
            # grab them in the same order you passed them into GroupChat
            writer, reviewer, parser = groupchat.agents
            msgs = groupchat.messages

            # 1) very first turn (no last_speaker yet)
            if last_speaker is None or not msgs:
                return writer

            # 2) after writer speaks → reviewer
            if last_speaker is writer:
                return reviewer

            # 3) after reviewer speaks → parser or back to writer
            if last_speaker is reviewer:
                last_content = msgs[-1].get("content", "")
                if "DONE!" in last_content:
                    return parser
                return writer

            if last_speaker is parser:
                return None
            if parser.is_terminated:
                return None

            # fallback: also stop
            return None

        chat = GroupChat(
            agents=[content_writer, content_reviewer, content_parser],
            speaker_selection_method=autogen_selector,
            messages=[],
            max_round=10,  # Increased to allow for multiple revision rounds
        )
        chat.reset()
        manager = GroupChatManager(
            name="group_manager",
            groupchat=chat,
            llm_config=llm_config,
        )

        manager.initiate_chat(
            recipient=content_writer,
            message=f"Content plan: {step.task}. Student already saw theory and cards {created_cards}",
            max_rounds=self.max_rounds,
        )

        # Get messages from both agents
        parser_msgs = [m for m in chat.messages if m["name"] == content_parser.name]
        rev_msgs = [m for m in chat.messages if m["name"] == content_reviewer.name]
        raw = parser_msgs[-1]["content"]
        if step.step_type == "theory":
            return Theory.parse_raw(raw)
        elif step.step_type in ("choice", "quiz"):
            return Choice.parse_raw(raw)
        elif step.step_type == "text_question":
            return TextQuestion.parse_raw(raw)

        return raw
