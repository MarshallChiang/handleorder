import json, datetime, re, requests, time
from  config import getID

'''
{
    ------OrderData------
    'merchantid' : '1258', (offer_id)
    'dc' : 'web',  (device)
    'ht' : '1496200372019', (transaction_unixtimestamp)
    'bh' : 'purchase', (behvaior)
    'tr' : '1800', (order_amount)
    'ti' : 'TG180221Q00004', (order_id)
    ----SKUDataOfOrder----
    r'pr+0-9+id': '4127124', (product_id)
    r'pr+0-9+pr': '395', (product_amount)
    r'pr+0-9+qt': '1', (product_quantity)
    ------OrderData------
    'tripid' : '102e1eea8d167d568adb3caa325971', (Hasoffers shoppingtrip)
    'ts' : '0' (status -- (0=make|1=cancel|2=refund|3=shipped))
}
'''
TEST_JSON = {
    'merchantid' : '741', 
    'ht' : (int(datetime.datetime.now().strftime("%s")) * 1000),
    'ti' : 'TG180221Q00004',
    'oid' : 'TS21012473284',
    'prid' : '4127124',
    'prtp' : '395',
    'tripid' : '1020ad06c1c8444be309d5d5eefd37',
    'osc' : 'cancel'
}


CPAs = ['2326', '2328']
def HttpsResponse(statusCode, Bol, Message) :
    
    return {
        'statusCode' : statusCode,
        'body' : json.dumps({
            'Success' : Bol,
            'Message' : Message
        })
    }

def lambda_handler(even, context) :
    print(even)
    data = even['queryStringParameters']
    if data :
        statusCode, Bol, Message = orderParse(data)
    else :
        return HttpsResponse(500, False, 'No Data Provided.')
    return HttpsResponse(statusCode, Bol, Message)

def orderParse(data) :
    
    if len(set(TEST_JSON.keys()) - set(data.keys())) != 0 or None in set(data.values()) :
        return 500, False, 'QueryString Format or Value Error.'
    else :
        params = dict()
        params['amount'] = data['prtp']
        params['timezone'] = 'Asia/Hong_Kong'
        try :
            params['datetime'] = datetime.datetime.utcfromtimestamp(int(data['ht'][:-3]) + 3600 * 8).strftime('%Y-%m-%d %H:%M:%S')
        except (TypeError, ValueError) :
            params['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if data['osc'] == 'create' :
            params['offer_id'] = getID(data['merchantid'], 'order')
            params['transaction_id'] = data['tripid']
        else :
            params['offer_id'] = getID(data['merchantid'], 'validation')
            params['aff_id'] = '1152'
            params.pop('datetime')
            params.pop('timezone')
            if data['osc'] in ('cancel', 'return') :
                params['status'] = 'rejected'
            else :
                params['status'] = 'approved'
        if not params['offer_id'] :
            return 500, False, 'Invalid StoreID.'
        params['adv_sub'] = data['oid'] if params['offer_id'] not in CPAs else data['ti']
        params['adv_sub2'] = data['ti'] if params['offer_id'] not in CPAs else data['oid']
        params['adv_sub3'] = data['prid']         
        return APIcall(params)
            
def APIcall(params) :
    url = 'http://shopback.go2cloud.org/aff_lsr'
    r = requests.get(url, params=params)
    print(params)
    print(r.text)
    response = r.text.split(';')        
    if response[1] != '' :
        errormessage = response[1]
        return 500, False, 'Internal Server Data Create Error. [%s]'%errormessage
    else :
        return 200, True, ''

if __name__ == '__main__' :
    event = {}
    event['queryStringParameters'] = TEST_JSON
    lambda_handler(event,{})
    #orderParse(TEST_JSON)
