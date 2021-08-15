import datetime, decimal, os
import json
import authorize
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY') 

_PRICE_ID_LIGHT = os.getenv('STRIPE_PRICE_ID_LIGHT')
_PRICE_ID_PREMIUM = os.getenv('STRIPE_PRICE_ID_PREMIUM')
_SUBSCRIPTION_PAGE_URL = os.getenv('SUBSCRIPTION_PAGE_URL')

_EVENT_KEY_PATH_PARAMETER = 'pathParameters'
_EVENT_KEY_QUERY_STRING_PARAMETER = 'queryStringParameters'
_EVENT_KEY_HTTP_METHOD = 'httpMethod'
_PARAM_KEY_PRICE_ID = 'price_id'


_RESPONSE_303 = {
        'statusCode': 303,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }

_RESPONSE_400 = {
        'statusCode': 400,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }

_RESPONSE_404 = {
        'statusCode': 404,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }

_RESPONSE_500 = {
        'statusCode': 500,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }


def create_checkout_session(price_id):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[
              'card',
            ],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=_SUBSCRIPTION_PAGE_URL + '?success=true',
            cancel_url=_SUBSCRIPTION_PAGE_URL + '?canceled=true',
        )
        return checkout_session.url
    except Exception as ex:
        print(ex)
        return None


def lambda_handler(event, context):
    print('event:', event)
    authed = authorize.is_authorized(event)
    if not authed:
        print('returning 403 as not authed.')
        return _RESPONSE_403

    query_string_parameters = event[_EVENT_KEY_QUERY_STRING_PARAMETER]
    print("query_string_parameters:", query_string_parameters)

    http_method = 'GET'
    if _EVENT_KEY_HTTP_METHOD in event:
        http_method = event[_EVENT_KEY_HTTP_METHOD]

    if http_method != 'POST':
        print('returning 400 as the method {m} is not POST.'.format(m = http_method))
        return _RESPONSE_400

    price_id = None
    if query_string_parameters:
        if _PARAM_KEY_PRICE_ID in query_string_parameters:
            price_id = query_string_parameters[_PARAM_KEY_PRICE_ID]

    redirect_url = create_checkout_session(price_id)
    if not redirect_url:
        print('could not retrieve the redirect url.')
        return _RESPONSE_500

    ret = _RESPONSE_303
    ret['headers']['Location'] = redirect_url
    return ret
