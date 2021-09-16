def getID(store_id, req_type):
    data =  {
            '741' : { #TEST
                'order' : '1544',
                'validation' : '1542'
            }    
        }
    if store_id not in data.keys() and req_type not in ['order','validation']:
        return None
    else :  
        return data[store_id][req_type]
