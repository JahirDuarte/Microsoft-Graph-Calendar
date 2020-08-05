# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tutorial.auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from tutorial.graph_helper import get_user, get_calendar_events
import dateutil.parser
import urllib
import json
import requests
import yaml

# <HomeViewSnippet>
def home(request):
  context = initialize_context(request)

  return render(request, 'tutorial/home.html', context)
# </HomeViewSnippet>

# <InitializeContextSnippet>
def initialize_context(request):
  context = {}

  # Check for any errors in the session
  error = request.session.pop('flash_error', None)

  if error != None:
    context['errors'] = []
    context['errors'].append(error)

  # Check for user in the session
  context['user'] = request.session.get('user', {'is_authenticated': False})
  return context
# </InitializeContextSnippet>

# <SignInViewSnippet>
def sign_in(request):
  # Get the sign-in URL
  sign_in_url, state = get_sign_in_url()
  # Save the expected state so we can validate in the callback
  request.session['auth_state'] = state
  # Redirect to the Azure sign-in page
  return HttpResponseRedirect(sign_in_url)
# </SignInViewSnippet>

# <SignOutViewSnippet>
def sign_out(request):
  # Clear out the user and token
  remove_user_and_token(request)

  return HttpResponseRedirect(reverse('home'))
# </SignOutViewSnippet>

# <CallbackViewSnippet>
def callback(request):
  # Get the state saved in session
  expected_state = request.session.pop('auth_state', '')
  print("expected_state", expected_state)
  # Make the token request
  token = get_token_from_code(request.get_full_path(), expected_state)
  print("token", token)
  # Get the user's profile
  user = get_user(token)
  print("user", user)
  # Save token and user
  store_token(request, token)
  store_user(request, user)

  return HttpResponseRedirect(reverse('home'))
# </CallbackViewSnippet>

# <CalendarViewSnippet>
def calendar(request):
  context = initialize_context(request)

  token = get_token(request)

  events = get_calendar_events(token)

  if events:
    # Convert the ISO 8601 date times to a datetime object
    # This allows the Django template to format the value nicely
    for event in events['value']:
      event['start']['dateTime'] = dateutil.parser.parse(event['start']['dateTime'])
      event['end']['dateTime'] = dateutil.parser.parse(event['end']['dateTime'])

    context['events'] = events['value']

  return render(request, 'tutorial/calendar.html', context)
# </CalendarViewSnippet>


def eventCreate(request):
    stream = open('oauth_settings.yml', 'r')
    settings = yaml.load(stream, yaml.SafeLoader)

    token = request.session['oauth_token']
    for element in token:
        print("TOKEN ELEMENT:", element)
    print("\n")

    owner=request.POST.get('owner','')
    subject=request.POST.get('subject','')
    date=request.POST.get('date','')
    start=request.POST.get('start','')
    end=request.POST.get('end','')
    print('DATE: ',date)

    newHeaders = {
      'Content-type': 'application/json', 
      'Accept': 'text/plain',
      'Authorization': 'Bearer ' + token['access_token'],
      'client_id' : settings['app_id'],
      'client_secret': settings['app_secret'],
    }
    url = 'https://graph.microsoft.com/v1.0/me/events'
    data = {
      "subject": owner,
      "subject": subject,
      "start": {
          "dateTime": date+"T"+"12:00:00",
          "timeZone": "Pacific Standard Time"
      },
      "end": {
          "dateTime": date+"T"+"12:00:00",
          "timeZone": "Pacific Standard Time"
      },
      "allowNewTimeProposals": True
    }

    data = json.dumps(data)
    print("\n1. Data1: ", data)

    # Convert string to byte
    data = data.encode('utf-8')
    print("\n2. Data2: ", data)

    response = requests.post(url,data,headers=newHeaders)
    
    print("Status code: ", response.status_code)

    response_Json = response.json()
    print("Printing Post JSON data")
    print(response_Json)
  
    #return render calendar
    return redirect('/calendar')