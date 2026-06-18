from dataclasses import dataclass, field


@dataclass
class InterviewSession:
    interview_type: str = "behavioral"
    total_questions: int = 5
    job_role: str = ""
    warmup_mode: bool = False

    questions_asked: list = field(default_factory=list)
    answers_given: list = field(default_factory=list)
    feedback_per_answer: list = field(default_factory=list)
    question_types: list = field(default_factory=list)
    answer_durations: list = field(default_factory=list)  # seconds per answer
    filler_counts: list = field(default_factory=list)     # dict per answer

    current_question_index: int = 0
    is_complete: bool = False

    # Warmup tracking
    warmup_questions_asked: int = 0
    warmup_complete: bool = False
    WARMUP_COUNT: int = 2

    @property
    def questions_remaining(self) -> int:
        return self.total_questions - self.current_question_index

    @property
    def current_question(self) -> str:
        return self.questions_asked[-1] if self.questions_asked else ""

    @property
    def current_question_type(self) -> str:
        return self.question_types[-1] if self.question_types else "behavioral"

    @property
    def is_in_warmup(self) -> bool:
        return self.warmup_mode and not self.warmup_complete

    def all_filler_totals(self) -> list:
        return [sum(d.values()) if d else 0 for d in self.filler_counts]

    def per_answer_scores(self) -> list:
        return [f.get("score", 0) for f in self.feedback_per_answer]
