from typing import  Dict, Any
import re


papi_features = [
    "PAPI_TOT_INS",
    "PAPI_TOT_CYC",
    "PAPI_L1_DCM",
    "PAPI_L2_DCM",
    "PAPI_L3_DCM",
    "PAPI_L1_TCM",
    "PAPI_L2_TCM",
    "PAPI_L3_TCM",
]

papi_features_name_mapping = {
    "PAPI_TOT_INS": "total_instructions",
    "PAPI_TOT_CYC": "total_cycles",
    "PAPI_L1_DCM": "l1_dcache_misses",
    "PAPI_L2_DCM": "l2_dcache_misses",
    "PAPI_L3_DCM": "l3_dcache_misses",
    "PAPI_L1_TCM": "l1_icache_misses",
    "PAPI_L2_TCM": "l2_icache_misses",
    "PAPI_L3_TCM": "l3_icache_misses",
}

def extract_hw_counters(output: str, loop_index: int) -> Dict[str, Any]:

    profiled_feature_index = loop_index
    if loop_index ==-1:
        profiled_feature_index = 0

    extracted_hw_counters = {}
    for feature in papi_features:
        feature_regex = re.compile(f"{feature}: (\d+)")
        feature_values = feature_regex.findall(output)
        feature_value = feature_values[profiled_feature_index]
        if feature_value:
            feature_name = papi_features_name_mapping[feature]
            extracted_hw_counters[feature_name] = int(feature_value[0])
    return extracted_hw_counters

def collect_profiled_features(output: str, loop_index: int) -> Dict[str, Any]:

    features = {}
    features_last_suffix= {}

    hw_counters_features = extract_hw_counters(output, loop_index)

    extracted_features = { ** hw_counters_features }

    for feature_name, profiled_value in extracted_features.items():        
        features[feature_name] = profiled_value
        features_last_suffix[feature_name] = 0
        
    return features