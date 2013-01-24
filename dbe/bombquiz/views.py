from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count, Avg
from django.http import Http404

from dbe.shared.utils import *
from dbe.bombquiz.models import *
from dbe.bombquiz.forms import *

from dbe.generic.base import TemplateView
from dbe.generic.edit import CreateView, FormView

seconds       = 30
lose_question = 20


class NewPlayer(CreateView):
    """Create new player & add data to session."""
    modelform_model               = PlayerRecord
    modelform_form_class          = NewPlayerForm
    modelform_context_object_name = "new_player"
    template_name                 = "question.html"
    success_url                   = reverse_lazy("question")

    def form_valid(self, form, modelform, _):
        resp = super(NewPlayer, self).form_valid(form, modelform, _)
        data = dict(player_record=self.modelform_object, question=1, left=seconds)
        self.request.session.update(data)
        return resp


class Done(TemplateView):
    template_name = "bombquiz/done.html"

    def add_context(self):
        return dict( left=self.request.session.get("left") )


class Stats(TemplateView):
    template_name = "stats.html"

    def add_context(self):
        answer    = PlayerRecord.obj.filter(passed=False).annotate( anum=Count("answers") )
        aggregate = answer.aggregate(avg=Avg("anum"))
        return dict(ans_failed=aggregate)


class QuestionView(FormView):
    form_class    = QuestionForm
    template_name = "question.html"

    def get_form_kwargs(self):
        """Get current section (container), init the form based on questions in the section."""
        kwargs      = super(QuestionView, self).get_form_kwargs()
        session     = self.request.session
        self.player = session.get("player_record")
        self.qn     = session.get("question", 1)
        if not self.player: raise Http404

        self.questions = Question.obj.all()
        if not self.questions: raise Http404

        self.question = self.questions[self.qn-1]
        return dict(kwargs, question=self.question)

    def form_valid(self, form, *args):
        """Create user answer records from form data."""
        session = self.request.session
        left    = session.get("left", seconds)
        answer  = form.cleaned_data.get("answer")
        correct = bool(answer == self.question.answer)

        # subtract time left and create the answer object
        if not correct:
            left -= lose_question
            session["left"] = left
        Answer.obj.create(question=self.question, player_record=self.player, correct=correct, answer=answer)

        # redirect to the next question or to 'done' page
        if self.qn >= self.questions.count() or left <= 0:
            self.player.update( passed=bool(left > 0) )
            return redir("done")
        else:
            session["question"] = session.get("question", 1) + 1
            return redir("question")

    def get_context_data(self, **kwargs):
        context = super(QuestionView, self).get_context_data(**kwargs)
        session = self.request.session
        return dict(context, qnum=self.qn, total=self.questions.count(), left=session["left"])
