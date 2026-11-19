"""Compute campaign rates from explicit impressions, reach, clicks and spend."""
import argparse
import csv
import json
import math

def ratio(value, denominator):
    return value / denominator if denominator else None

def calculate(row):
    impressions, reach, interactions, clicks = (int(row[key]) for key in ('impressions','reach','interactions','clicks'))
    spend = float(row['spend_uah'])
    if min(impressions, reach, interactions, clicks, spend) < 0 or not math.isfinite(spend):
        raise ValueError('Counts and spend must be finite and nonnegative')
    if max(reach, clicks) > impressions:
        raise ValueError('Reach and unique link clicks cannot exceed impressions in this example')
    return {'variant':row['variant'], 'impressions':impressions,
            'ctr':ratio(clicks, impressions), 'er':ratio(interactions, reach), 'cpc':ratio(spend, clicks)}

def compare(a, b):
    if a['ctr'] is None or b['ctr'] is None:
        return None
    p, q = a['ctr'], b['ctr']
    delta = q-p
    error = 1.96*math.sqrt(p*(1-p)/a['impressions']+q*(1-q)/b['impressions'])
    return {'ctr_delta_pp': delta*100, 'relative_change': ratio(delta,p),
            'approximate_95pct_ci_pp':[(delta-error)*100,(delta+error)*100],
            'assumption':'Independent impressions; example data only'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path')
    args=parser.parse_args()
    with open(args.csv_path,encoding='utf-8-sig',newline='') as file:
        rows=[calculate(row) for row in csv.DictReader(file)]
    result={'variants':rows,'comparison':compare(*rows) if len(rows)==2 else None}
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
