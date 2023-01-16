from django import forms
from django.conf import settings
from google.cloud import recaptchaenterprise_v1

class GRecaptchaForm(forms.Form):
  def __init__(self, *args, **kwargs):
    self.risk_score = 0
    if len(args) > 0:
      self.recaptcha = args[0].get('g-recaptcha-response',None)
    else:
      self.recaptcha = None
    super(forms.Form, self).__init__(*args, **kwargs)

  def is_valid(self):
    assessment = self._create_assessment(
      project_id=settings.GOOGLE_RECAPTCHA_PROJECT_ID,
      recaptcha_site_key=settings.GOOGLE_RECAPTCHA_SITE_KEY,
      token=self.recaptcha,
      recaptcha_action='form') # matches data-action on HTML page

    self.risk_score = assessment.risk_analysis.score 
    return super(forms.Form, self).is_valid()

  #https://cloud.google.com/recaptcha-enterprise/docs/create-assessment
  def _create_assessment(self, project_id: str, recaptcha_site_key: str, token: str, recaptcha_action: str) -> recaptchaenterprise_v1.Assessment:
    """Create an assessment to analyze the risk of a UI action.
    Args:
      project_id: GCloud Project ID
      recaptcha_site_key: Site key obtained by registering a domain/app to use recaptcha services.
      token: The token obtained from the client on passing the recaptchaSiteKey.
      recaptcha_action: Action name corresponding to the token.
    """

    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    # Set the properties of the event to be tracked.
    event = recaptchaenterprise_v1.Event()
    event.site_key = recaptcha_site_key
    event.token = token

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_name = f"projects/{project_id}"

    # Build the assessment request.
    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    response = client.create_assessment(request)

    # Check if the token is valid.
    if not response.token_properties.valid:
        print(
            "The CreateAssessment call failed because the token was "
            + "invalid for for the following reasons: "
            + str(response.token_properties.invalid_reason)
        )
        return

    # Check if the expected action was executed.
    if response.token_properties.action != recaptcha_action:
        print(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return
    else:
        # Get the risk score and the reason(s)
        # For more information on interpreting the assessment,
        # see: https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment
        for reason in response.risk_analysis.reasons:
            print(reason)
        print(
            "The reCAPTCHA score for this token is: "
            + str(response.risk_analysis.score)
        )
        # Get the assessment name (id). Use this to annotate the assessment.
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")
    return response
