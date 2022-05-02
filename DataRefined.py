#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 14:00:45 2022

@author: benjaminbowring
"""

import pandas as pd

transact_df = pd.read_csv('transact_data.csv')
acc_df = pd.read_excel('AccCompliance.xlsx')
jan_comp = pd.read_excel('JanCompTrimmed.xlsx')
operators_df = pd.read_excel('operators.xlsx')

acc_df = acc_df[~acc_df['INSTALLATION_IDENTIFIER'].isnull()].copy()

acc_df['ICIS-ID'] = acc_df['REGISTRY_CODE'] + '-' + acc_df['INSTALLATION_IDENTIFIER'].astype(int).astype(str)

clean_transact = transact_df.copy()
clean_transact['NEW_ID_TRANSFER'] = clean_transact['TRANSFERRING_ACCOUNT_HOLDER_COUNTRY_CODE'].astype(str) + '-' + clean_transact['TRANSFERRING_ACCOUNT_IDENTIFIER'].dropna().astype(int).astype(str)
clean_transact['NEW_ID_RECEIVE'] = clean_transact['ACQUIRING_ACCOUNT_HOLDER_COUNTRY_CODE'].astype(str) + '-' + clean_transact['TRANSFERRING_ACCOUNT_IDENTIFIER'].dropna().astype(int).astype(str)

# =============================================================================
# Unified DF
# =============================================================================

df_ids = jan_comp[['Permit identifier', 'ICIS-ID', 'Installation name']].copy()

df_ids['PERMIT_MATCH_TRANSFER'] = df_ids['Permit identifier'].isin(clean_transact['TRANSFERRING_INSTALLATION_PERMIT_IDENTIFIER']).astype(int)
df_ids['ICIS_MATCH_TRANSFER'] = df_ids['ICIS-ID'].isin(clean_transact['NEW_ID_TRANSFER']).astype(int)
df_ids['NAME_MATCH_TRANSFER'] = df_ids['Installation name'].isin(clean_transact['TRANSFERRING_ACCOUNT_NAME']).astype(int)

df_ids['PERMIT_MATCH_ACQUIRE'] = df_ids['Permit identifier'].isin(clean_transact['ACQUIRING_INSTALLATION_PERMIT_IDENTIFIER']).astype(int)
df_ids['ICIS_MATCH_ACQUIRE'] = df_ids['ICIS-ID'].isin(clean_transact['NEW_ID_RECEIVE']).astype(int)
df_ids['NAME_MATCH_ACQUIRE'] = df_ids['Installation name'].isin(clean_transact['ACQUIRING_ACCOUNT_NAME']).astype(int)

df_ids['MATCH'] = (df_ids[['PERMIT_MATCH_TRANSFER', 'ICIS_MATCH_TRANSFER', 'NAME_MATCH_TRANSFER',
                           'PERMIT_MATCH_ACQUIRE', 'ICIS_MATCH_ACQUIRE', 'NAME_MATCH_ACQUIRE']].sum(axis = 1) > 0).astype(int)

id_lookup_dict = {'PERMIT_MATCH_TRANSFER': 'Permit identifier',
                  'PERMIT_MATCH_ACQUIRE': 'Permit identifier',
                  'ICIS_MATCH_TRANSFER': 'ICIS-ID',
                  'ICIS_MATCH_ACQUIRE': 'ICIS-ID',
                  'NAME_MATCH_TRANSFER': 'Installation name',
                  'NAME_MATCH_ACQUIRE': 'Installation name'}

matched_ids = df_ids.copy()

for col in id_lookup_dict:

    matched_ids[col] = matched_ids[id_lookup_dict[col]][matched_ids[col].astype(bool)]
    

trial_df = matched_ids[[x for x in id_lookup_dict]].bfill(axis = 1)



transfer_columns = ['TRANSFERRING_INSTALLATION_PERMIT_IDENTIFIER', 'NEW_ID_TRANSFER', 'TRANSFERRING_ACCOUNT_NAME']
clean_transact[transfer_columns].isin(trial_df['PERMIT_MATCH_TRANSFER'].dropna().values)
