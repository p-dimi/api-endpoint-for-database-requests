from django.shortcuts import render

from .models import ClicksInfo
#from .serializers import ClicksInfoSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json

from datetime import date
#import datetime

class ViewClicksInfo(APIView):
    name = 'View clicks info'
    description = 'Shows clicks database info based on API flags'
    
    model_columns = ['date','channel','country','os','impressions','clicks','installs','spend','revenue', 'cpi']
    
    numerical_columns = ['date', 'impressions', 'clicks', 'installs', 'spend', 'revenue', 'cpi']

    '''
    API FLAGS:
    
    datefrom=yyyy-mm-dd or earliest
    dateto=yyyy-mm-dd or latest
    columns=date,channel,country,os,impressions,clicks,installs,spend,revenue
    group=date,channel,country,os,impressions,clicks,installs,spend,revenue
    sorted=column_name,ascending or descending
    cpi=true or false
    include_only=any string
    
    divider: &
    '''
    
    def api_parser(self, api_flags):
        # parses api string and returns dictionary of rules by which to organize the data being requested
        
        # default rules
        rules = {
                'date_from':['earliest'],
                'date_to':['latest'],
                'columns':['date','channel','country','os','impressions','clicks','installs','spend','revenue'],
                'group':[],
                'sorted':['date','descending'],
                'cpi':['false'],
                'include_only':[]
                }
        
        # if api_flags is blank, return default view and True status for no problems with URL
        if api_flags == '':
            return rules, True
        else:
            # parse api flags
            if len(api_flags) > 1:
                # proceed with parsing
                flags = api_flags.split('&')
                
                flags = [flag.split('=') for flag in flags]
                
                flags = [(flag[0], flag[1].split(',')) for flag in flags]
                
                # try to create rules dict based on parsed flags, if key doesn't exist - return empty dict and False status
                try:
                    for tup in flags:
                        rules[tup[0]] = tup[1]
                    return rules, True
                
                except:
                    return {}, False
                
            else:
                # return empty dict and False status for URL problem (URL incorrect)
                return {}, False
    
    def rules_validator(self, rules):
        # validates rules dictionary
        '''
        if non-existing columns are requested in sorted, group, or columns, or if invalid commands are requested, validation will break
        
        example of invalid command:
        sort=date,blescending <- where blescending is neither ascending nor descending
        
        validation will pass over all rules, and provide detailed errors log if there are errors
        '''
        
        errors={}
        error_counter = 0
        
        # validate date_from and date_to
        if rules['date_from'][0] == 'earliest':
            # if earliest set to arbitrary very long-ago date
            rules['date_from'] = (1000,1,1)        
        else:
            try:
                # it is expected the format is yyyy-mm-dd
                # if it is not - add to errors
                year,month,day = rules['date_from'][0].split('-')
                rules['date_from'] = (int(year), int(month), int(day))
            except:
                errors[error_counter] = 'date_from is in wrong format. Format expected is yyyy-mm-dd or the word earliest. Requested format is {}'.format(rules['date_from'][0])
                error_counter += 1
                
        if rules['date_to'][0] == 'latest':
            # if latest set to arbitrary far future date
            rules['date_to'] = (3000,12,30)        
        else:
            try:
                # it is expected the format is yyyy-mm-dd
                # if it is not - add to errors
                year,month,day = rules['date_to'][0].split('-')
                rules['date_to'] = (int(year), int(month), int(day))
            except:
                errors[error_counter] = 'date_to is in wrong format. Format expected is yyyy-mm-dd or the word latest. Requested format is {}'.format(rules['date_to'][0])
                error_counter += 1
    
        # validate columns
        # confirm that requested columns actually exist 
        for item in rules['columns']:
            if item not in self.model_columns:
                # if does not exist - add to error
                errors[error_counter] = 'columns is incorrect. Format expected is valid column names separated by comma. Columns must be of the following: {}. Requested columns is {}'.format(self.model_columns, rules['columns'][0])
                error_counter += 1
                
        # validate group
        # confirm that requested grouping columns actually exist and are also in requested columns
        for item in rules['group']:
            if item not in self.model_columns:
                # if does not exist - add to error
                errors[error_counter] = 'group is incorrect. Format expected is valid column names separated by comma. Columns must be of the following: {}. Requested group is {}'.format(self.model_columns, rules['group'][0])
                error_counter += 1
            # check if column grouped by is in requested columns, and if not - add it to requested columns
            if item in self.model_columns and item not in rules['columns']:
                # if not in requested columns, add to requested columns
                rules['columns'].append(item)
        
        # validate sorted
        if len(rules['sorted']) != 2 or rules['sorted'][0] not in self.model_columns or rules['sorted'][1] not in ['ascending','descending']:
            # insufficient arguments in sorted, or an incorrect column / argument - return error
            errors[error_counter] = 'sorted is incorrect. Format expected is valid column name and the argument ascending or the argument descending, separated by comma. Columns must be of the following: {}. Requested sorted is {}'.format(self.model_columns ,rules['sorted'][0])
            error_counter += 1
        else:
            # if sorted column not showing up in columns already - add it
            # if sorting by a column, it is assumed the column is requested, even if not specified in columns
            if rules['sorted'][0] not in rules['columns']:
                rules['columns'].append(rules['sorted'][0])
        
        # validate cpi
        if rules['cpi'][0] not in ['true','false']:
            # incorrect cpi argument
            errors[error_counter] = 'cpi is incorrect. Format expected is the argument true or the argument flase. Requested cpi is {}'.format(rules['cpi'][0])
            error_counter += 1
        else:
            if rules['cpi'][0] == 'true':
                rules['cpi'] = True
                # also add cpi to columns if not already there
                if 'cpi' not in rules['columns']:
                    rules['columns'].append('cpi')
                
            elif rules['cpi'][0] == 'false':
                # confirm that cpi is not a requested column in columns or groups or sorted. if it is - assume cpi should also be true
                if 'cpi' in rules['columns'] or 'cpi' in rules['group'] or rules['sorted'][0] == 'cpi':
                    rules['cpi'] = True
                else:
                    rules['cpi'] = False

        # include_only is a special argument and does not undergo validation, as it allows flexibly inputting any string at all
                    
        # if there were any errors - return error dict and False validation status.
        if error_counter > 0:
            return errors, False
        else:
            # otherwise - return validated rules dictionary and True validation status
            return rules, True
    
    def group_models(self, models, grouping_columns):
        grouped_models_set = []
        
        groups = {}

        for model_obj in models:
            # get the grouping attributes
            attributes = []
            for col in grouping_columns:
                attribute = model_obj[col]
                attributes.append(attribute)
            
            # add the attribute(s) to the groups dictionary as keys
            # if that key already exists = instead add the model_obj to the group under that key
            key = '-'.join(attributes)
            if key in groups:
                groups[key].append(model_obj)
            else:
                groups[key] = [model_obj]
        
        # the groups dictionary should now have all the grouped model objects
        # the information is not being summed, as this will lead to the loss of information in requested columns that are not in the grouping columns
        
        # create a new models set based on the groups
        for key in groups:
            grouped_models_set.extend(groups[key])

        # return new models set, that is grouped
        return grouped_models_set
    
    def exclude_columns(self, models, columns):
        excluded_column_models = []
        
        for model_obj in models:
            for c in self.model_columns:
                if c not in columns:
                    del model_obj[c]
                    # I am also not interested in id, if it is still there
                    try:
                        del model_obj['id']
                    except:
                        pass
            excluded_column_models.append(model_obj)
            
        return excluded_column_models
    
    def execute_rules(self, rules, models):
        # executes rules dictionary
        '''
        the executioner is meant to be robust even in the case of mismatched flags
        
        EXECUTION ORDER:
        
        1. date_from and date_to
        2. cpi
        3. sorted
        4. group
        5. columns
        6. include_only <- special case, due to flexibility of input
        '''
        
        # execute date_from and date_to
        # init indices list of which indeces represent the model objects that fit between date_from and date_to
        indeces=[]
        for index in range(len(models)):
            model_object = models[index]
            
            year,month,day = model_object['date'].split('-')
            
            # convert to date format for comparison
            low_date = date(rules['date_from'][0], rules['date_from'][1], rules['date_from'][2])
            high_date = date(rules['date_to'][0], rules['date_to'][1], rules['date_to'][2])
            model_date = date(int(year),int(month),int(day))
            
            # check if model date between date_from and date_to
            if low_date <= model_date <= high_date:
                indeces.append(index)

        # only get models fulfilling date_from and date_to
        models = [models[index] for index in indeces]
        
        # execute cpi
        if rules['cpi'] == True:
            for model_object in models:
                spend = model_object['spend']
                installs = model_object['installs']
                
                # account for 0 installs possibility to avoid division by zero
                if int(installs) == 0:
                    installs = 1
                
                # cpi = spend / installs
                cpi = float(spend) / int(installs)

                model_object['cpi'] = str(cpi)
        
        # execute sorted
        if rules['sorted'][1] == 'ascending':
            reverse = False
        elif rules['sorted'][1] == 'descending':
            reverse = True
        
        if rules['sorted'][0] in self.numerical_columns:
            # if it's numerical, the attribute must be converted first to an appropriate data format
            if rules['sorted'][0] == 'date':
                # if it's a date - format the date to a tuple of three integers in the lambda
                models.sort(key = lambda obj:  (int(obj[rules['sorted'][0]].split('-')[0]) , int(obj[rules['sorted'][0]].split('-')[1]) , int(obj[rules['sorted'][0]].split('-')[2])) , reverse = reverse)
            
            elif rules['sorted'][0] == 'spend' or rules['sorted'][0] == 'revenue' or rules['sorted'][0] == 'cpi':
                # if it's one of the float values - format to float
                models.sort(key = lambda obj: float(obj[rules['sorted'][0]]), reverse = reverse)
                
            else:
                # if it's one of the integer values - format to integer
                models.sort(key = lambda obj: int(obj[rules['sorted'][0]]), reverse = reverse)
        else:
            models.sort(key = lambda obj: obj[rules['sorted'][0]], reverse = reverse)
        
        # execute group
        # only group if there are grouping columns specified
        if len(rules['group']) > 0:
            models = self.group_models(models, rules['group'])
        
        # execute columns
        models = self.exclude_columns(models, rules['columns'])
        
        # execute include_only
        if len(rules['include_only']) > 0:
            models = self.include_only(models, rules['include_only'])
        
        # rules execution complete - return queryset
        return models
    
    def include_only(self, models, include_only_list):
        # will go over the models and check if they contain all the items in the include_only_list
        # if they do not - remove them from queryset

        # convert include_only_list into dict of booleans
        incl_dict = {}
        for item in include_only_list:
            incl_dict[item] = False
        
        indeces=[]
        for index in range(len(models)):
            model_obj = models[index]
            # make local_incl_dict as copy of the baseline incl_dict
            local_incl_dict = incl_dict.copy()
            
            # iterate over each item and mark in local_incl_dict if True
            for item in include_only_list:     
                for key in model_obj:
                    # count if the item occurs in the model_obj
                    if model_obj[key] == item:
                        local_incl_dict[item] = True
            
            # if all items in local_incl_dict are True - append this index
            append_index = all(value == True for value in local_incl_dict.values())

            if append_index == True:
                indeces.append(index)

        # return only models subscribing to include_only
        models = [models[index] for index in indeces]
        return models
            
    def get(self, request, api_flags=''):
        # parse api flags  
        rules, parsing_status = self.api_parser(api_flags)

        if parsing_status == False:
            # parsing failed, return 400 bad request
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # validate rules
        rules, validation_status = self.rules_validator(rules)
        
        if validation_status == False:
            # validation failed, return errors and 400 bad request
            errors = json.dumps(rules)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        # load models, as value dicts
        queryset = list(ClicksInfo.objects.all().values())
       
        # execute rules
        queryset = self.execute_rules(rules, queryset)

        # return requested data
        return Response(queryset)