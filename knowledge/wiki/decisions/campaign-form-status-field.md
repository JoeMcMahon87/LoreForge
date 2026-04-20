# CampaignForm — Status Field Not Required

## Decision

`CampaignForm` includes `status` in `fields` but sets `self.fields["status"].required = False` in `__init__`.

## Why

The template hides the status field on create (only shown on edit via `{% if form.instance.pk %}`). Without marking it not-required, a POST without `status` fails form validation and returns 200 instead of redirecting — the form silently fails.

The model default (`active`) applies when the field is empty on save.

## How to apply

Any `ModelForm` where a field is hidden in the template for some states but still included in `fields` must have `required = False` set in `__init__`, or the form will reject submissions that don't include it.
