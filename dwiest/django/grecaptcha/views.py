from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView
from .forms import GRecaptchaForm

class GRecaptchaView(FormView):
  template_name = "index.html"
  success_url = '.'
  form_class = GRecaptchaForm

  def get(self, request, *args, **kwargs):
    print("GRecaptchaView.get()")
    form = GRecaptchaForm()
    return render(request, self.template_name, {'form': form})

  def post(self, request, *args, **kwargs):
    print("GRecaptchaView.post()")
    form = GRecaptchaForm(request.POST)
    if form.is_valid():
      request.session['risk_score'] = form.risk_score
      return HttpResponseRedirect(request.path)
      #return render(request, self.template_name, {'form': form})
    else:
      return render(request, self.template_name, {'form': form})
