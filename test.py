from __future__ import print_function

from urllib2 import Request, urlopen, URLError
import json
import datetime


surf_spot = '117'

def surfs_up(surf_spot):
    request = Request('http://api.spitcast.com/api/spot/forecast/' + surf_spot)
    response = urlopen(request)
    
    surf_report = response.read()
    parsed_json = json.loads(surf_report)
    #print parsed_json
    
    now = datetime.datetime.now()
    h = now.hour
    postfix = 'AM'
    if h > 12:
       postfix = 'PM'
       h -= 12
    hourX = '{}{}'.format(h or 12,postfix)

    timeDict = {
        '12AM': 16,
        '1AM': 17,
        '2AM': 18,
        '3AM': 19,
        '4AM': 20,
        '5AM': 21,
        '6AM': 22,
        '7AM': 23,
        '8AM': 0,
        '9AM': 1,
        '10AM': 2,
        '11AM': 3,
        '12PM': 4,
        '1PM': 5,
        '2PM': 6,
        '3PM': 7,
        '4PM': 8,
        '5PM': 9,
        '6PM': 10,
        '7PM': 11,
        '8PM': 12,
        '9PM': 13,
        '10PM': 14,
        '11PM': 15,
    }

    t  = timeDict[hourX]
    #surfreport = hourX
    spot = parsed_json[t]['spot_name']
    swell = parsed_json[t]['size']
    cond = parsed_json[t]['shape_full']

    if cond == "Poor-Fair":
        cond = "sloppy"
    elif cond == "Poor":
        cond = "sloppy"
    elif cond == "Fair":
        cond = "surfable"
    elif cond == "Fair-Good":
        cond = "surfable"
    elif cond == "Good":
        cond = "glassy"
    else:
        cond = cond

    surfreport = "The waves at " + str(spot) + " are currently " + str(swell) + " feet high with " + cond + " conditions."
    return surfreport
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    """
    if (event['session']['application']['applicationId'] !=
            ""):
        raise ValueError("Invalid Application ID")
    """
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MyColorIsIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        intent_name = "MyColorIsIntent"
        intent = "something"
        return set_color_in_session(intent, session)
        #raise ValueError("Invalid on_intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hey Bro, I can tell you surf reports of popular spots in California. To get started just say something like, tell me the surf report at mavericks." 
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your surf spot by saying, " \
                    "my surf spot is Mavericks."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    try:
        if 'value' in intent['slots']['Color']:
            favorite_color = intent['slots']['Color']['value']
            session_attributes = create_favorite_color_attributes(favorite_color)
            if intent['slots']['Color']['value']:
                if intent['slots']['Color']['value'] in dict:
                    #surf_spot = '119'
                    try:
                        keyo = intent['slots']['Color']['value']
                        surf_spot = str(dict[keyo])
                        speech_output = surfs_up(surf_spot)
                        should_end_session = True
                        reprompt_text = None
                    except:
                        speech_output = "I dont know the surf report at that spot yet. You can try another spot in California."
                        reprompt_text = "You can get the surf report by saying something like, tell me the surf report at steamer lane."
                elif intent['slots']['Color']['value'] == 'stop':
                    should_end_session = True
                    speech_output = "Goodbye"
                    reprompt_text = None
                elif intent['slots']['Color']['value'] == 'cancel':
                    should_end_session = True
                    speech_output = "Goodbye"
                    reprompt_text = None
                elif intent['slots']['Color']['value'] is None:
                    should_end_session = True
                    speech_output = "ummm okay"
                    reprompt_text = None
                    
                else: 
                    speech_output = 'I dont know the surf report at that spot yet. You can try another spot in California.'
                    reprompt_text = 'You can get the surf report by saying something like, tell me the surf report at steamer lane.'
                    should_end_session = False
            else:
                speech_output = "Talk to you later."
                reprompt_text = None
                should_end_session = True
        else:
            speech_output = "Im not sure what surf spot you said. "
            reprompt_text = "Im not sure what spot you said.. You can tell me what report you want by saying, tell me the surf report at huntington pier"
            should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    except:
        speech_output = "Im not sure what surf spot you said. Can you try again? "
        reprompt_text = "Im not sure what spot you said.. You can tell me what report you want by saying, tell me the surf report at huntington pier"
        should_end_session = False
        


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Have fun surfing "
        should_end_session = True
    else:
        speech_output = "I'm not sure what surf spot you said. Can you say the spot again? "
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Surfable - ',
            'content': 'Surf report - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
dict = {
        'fort point': 113,
        'eagles point': 649,
        'deadmans': 648,
        'kellys cove': 697,
        'north ocean beach': 114,
        'south ocean beach': 117,
        'linda mar': 120,
        'montara': 121,
        'mavericks': 122,
        'princeton jetty': 123,
        'pomponio state beach': 126,
        'ano nuevo': 118,
        'county line': 593,
        'waddell creek': 129,
        'waddell reefs': 600,
        'scotts creek': 128,
        'davenport landing': 133,
        'four mile': 131,
        'three mile': 130,
        'natural bridges': 6,
        'stockton avenue': 146,
        'swift street': 145,
        'getchell': 10,
        'mitchells cove': 144,
        'steamer lane': 2,
        'cowells': 3,
        'the rivermouth': 143,
        'blacks': 9,
        'santa marias': 8,
        '26th avenue': 7,
        'little windansea': 138,
        'rockview': 137,
        'sewer peak': 5,
        'pleasure point': 1,
        '38th avenue': 4,
        'the hook': 147,
        'sharks cove': 148,
        'capitola jetties': 149,
        'manresa': 150,
        'moss landing state beach': 161,
        'carmel beach': 154,
        'sand dollar': 152,
        'morro rock': 163,
        'pismo beach pier': 162,
        'jalama': 185,
        'refugio': 620,
        'sands': 182,
        'devereux': 181,
        'campus point': 179,
        'leadbetter': 177,
        'rincon': 198,
        'mondos': 193,
        'emma wood': 191,
        'c street': 190,
        'county line': 207,
        'zuma beach': 206,
        'malibu': 205,
        'topanga': 388,
        'venice': 204,
        'el porto': 402,
        'manhattan beach': 203,
        'hermosa': 202,
        'torrance beach': 200,
        'seal beach pier': 222,
        'surfside jetty': 602,
        'anderson st': 603,
        'bolsa chica': 604,
        'goldenwest': 220,
        '17th street': 605,
        'huntington pier': 221,
        'huntington beach': 643,
        '56th street': 219,
        '40th street': 607,
        '36th street': 608,
        'blackies': 651,
        'newport pier': 609,
        'the wedge': 217,
        'salt creek': 214,
        'doheny': 213,
        'san clemente pier': 212,
        't street': 211,
        'lasuen': 391,
        'riviera': 644,
        'calafia': 645,
        'state park': 392,
        'north gate': 210,
        'cottons point': 209,
        'upper trestles': 623,
        'lower trestles': 208,
        'church': 625,
        'san onofre': 239,
        'oceanside harbor': 238,
        'oceanside pier': 594,
        'wisconsin': 628,
        'cassidy': 629,
        'tamarack': 237,
        'warm water jetty': 596,
        'terra mar': 597,
        'campground': 630,
        'ponto': 236,
        'grandview': 400,
        'beacons': 235,
        'd street': 401,
        'swamis': 234,
        'cardiff reef': 232,
        '15th street - del mar': 230,
        'blacks beach': 229,
        'scripps pier': 228,
        'windansea': 227,
        'bird rock': 398,
        'tourmaline': 399,
        'pacific beach': 226,
        'mission beach': 397,
        'ocean beach pier': 225,
        'sunset cliffs': 224,
        'imperial beach': 223
    }
