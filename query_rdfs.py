# -*- coding: utf-8 -*-
import sys
import os
import json
import re

sys.path.append(os.path.join(os.path.dirname("__file__"), '..'))
current_dir = os.path.dirname("__file__")
current_dir = current_dir if current_dir is not '' else '.'
# directory to scan for any owl files
data_dir_path = current_dir + '/data_after_clean'


with open(data_dir_path + "/result_after_clean.json", 'r')as f:
    search = json.load(f)

#
# ─── QUERY DEF ──────────────────────────────────────────────────────────────────
#


# {'label': 'Táo', 'type': 'Fruits', 'has_calo': '52'}
def food_attribute(label):
    result = {"label": label, "Has_Nutrient": [], "Not_Use_Together": []}

    for content in search:
        if content["label"] == label and content['p'] == "type" and content['o'] != "NamedIndividual":
            result["type"] = content['o']
            target_index = search.index(content)
            text_tamp_next = search[target_index:]
            break
    for content in text_tamp_next:
        if content["label"] == label:
            if content['p'] != "Has_Nutrient" and content['p'] != "Not_Use_Together":
                result[content['p']] = content['o']
            else:
                result[content['p']].append(content['o'])
    return result

def nutrient_attribute(label):
    result = {"label": label}

    for content in search:
        if content["label"] == label and content['p'] == "type" and content['o'] != "NamedIndividual":
            result["type"] = content['o']
            target_index = search.index(content)
            text_tamp_next = search[target_index:]
            break
    for content in text_tamp_next:
        if content["label"] == label:
            result[content['p']] = (content['o'])
    return result


# {'label': '35.00-39.99', 'type': 'Body_Mass_Index_Range', 'value': 'Béo_phì_độ_2'}
def has_value(label):
    result = {}
    result["label"] = label
    for content in search:
        if content["label"] == label and content['p'] == "type" and content['o'] != "NamedIndividual":
            result["type"] = content['o']
            target_index = search.index(content)
            text_tamp_next = search[target_index:]
            break
    if result["type"] == "Physical_Activity_Level":
        for content in text_tamp_next:
            if content["label"] == label and content["p"] == "Has_Activity_Level_Range":
                result["value"] = content['o']
    elif result["type"] == "Body_Mass_Index_Range":
        for content in text_tamp_next:
            if content["label"] == label and content["p"] == "Has_Body_Mass_Index_Level":
                result["value"] = content['o']
    return result

# def BMI_value_calc(height,weight):


def BMI_range_calc(value):
    if value == 40:
        return "40.00"

    result = []
    tamp = None
    for content in search:
        if content['p'] == "type" and content['o'] == 'Body_Mass_Index_Range':
            tamp = content["label"]
            try:
                result.append(list(map(float, tamp.split("-"))))
            except:
                pass
    for content in result:
        if content[0] <= value <= content[1]:
            tamp = content
    result = "{0:.2f}-{1:.2f}".format(tamp[0], tamp[1])
    return result


def BMI_level_calc(range):  # Thiếu_cân_rất_nặng
    return has_value(range)["value"]


#
# ─── --- ────────────────────────────────────────────────────────────────────────
#

    
def extract_person_information(person):
    result = {}
    result["Person"] = person
    for content in search:
        if content["label"] == person and content["p"] != "type":
            result[content['p']] = content['o']
    return result


def check_individual_exist(name):
    flag = True
    for content in search:
        if content["label"] == name and content["o"] == "NamedIndividual":
            flag = False
            break
    return flag

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def avoided_group_food(illness):
    group_food = []
    result = []
    for content in search:
        if content["label"] == illness and content["p"] == "Avoid_Group_Food":
            group_food .append(content["o"])
    for food_item in group_food:
        for content in search:
            if content["label"] == food_item and content["p"] == "Has_Food":
                result.append(content["o"])
    return result


def needed_group_food(illness):
    group_food = []
    result = []
    for content in search:
        if content["label"] == illness and content["p"] == "Need_Group_Food":
            group_food .append(content["o"])
        if content["label"] == illness and content["p"] == "Need_Food":
            result.append(content["o"])
    for food_item in group_food:
        for content in search:
            if content["label"] == food_item and content["p"] == "Has_Food":
                result.append(content["o"])
    return result


def limit_food(illness):
    result = []
    for content in search:
        if content["label"] == illness and content["p"] == "Limit_Food":
            result.append(content["o"])
    return result


#
# ─── ---- ───────────────────────────────────────────────────────────────────────
#


def illness_list():
    result = []
    for content in search:
        if content["p"] == "type" and content["o"] == "Illness":
            result.append(content["label"])

    return result

def all_food():
    types = []
    result = []
    for content in search:
        if content["p"] == "subClassOf" and content["o"] == "Food_Items":
            types.append(content["label"])
    for content in search:
        if content["p"] == "type" and (content["o"] in types):
            try:
                food_attrb = food_attribute(content["label"])
                if food_attrb["Not_Use_Together"] != []:
                    result.append(str(food_attrb["label"]) + "|" + str(food_attrb["type"]) + "|" +
                                    str(food_attrb["Has_calo"]) + "|" + str(food_attrb["Not_Use_Together"]))
                else:
                    result.append(str(food_attrb["label"]) + "|" + str(food_attrb["type"]) + "|" +
                                    str(food_attrb["Has_calo"]) + "|")
            except:
                pass
            
    return result

def food_nutrient():
    food = []
    nutrient = []
    for content in search:
        if content["p"] == "Has_calo":
            food.append(content["label"])

    for content in search:
        if content['p'] == "Has_lack_of_sb_effect":
            nutrient.append(content["label"])
    return food, nutrient

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#

def condtion_for_rule_meal(food_default, list_only_food):
    result = []
    for food in food_default:
        if food in list_only_food:
            result.append(food)
    return result

def destructure_rule_meal(content, list_only_food):
    result = {}
    food_list = re.findall(r'\[(.*?)\]', content)
    for food_attrb in food_list:
        food = food_attrb.split(",")
        if "{" in food[1]:
            food[1] = food[1].replace("}", "")
            food_default = food[1].split("{")[1]
            food_default = food_default.split("|")
            # return result{"fix": ["food_name", "portion", "quanity"]}
            result["fix"] = [condtion_for_rule_meal(
                food_default, list_only_food), float(food[0]), int(food[2])]
        else:
            result[food[1]] = [float(food[0]), int(food[2])]
    return result


def list_structure_breakfast(list_food):
    list_rule = []
    for content in search:
        if content["label"] == 'StructureOfBreakFast' and content["p"] == "Has_structure":
            list_rule.append(destructure_rule_meal(
                content["o"], list_food))
    return list_rule


def list_structure_dinner(list_food):
    list_rule = []
    for content in search:
        if content["label"] == 'StructureOfDinner' and content["p"] == "Has_structure":
            list_rule.append(destructure_rule_meal(
                content["o"], list_food))
    return list_rule


def list_structure_lunch(list_food):
    list_rule = []
    for content in search:
        if content["label"] == 'StructureOfLunch' and content["p"] == "Has_structure":
            list_rule.append(destructure_rule_meal(
                content["o"], list_food))
    return list_rule


if __name__ == "__main__":
    # print(food_attribute("Cơm"))
        # if sys.argv[1] == "food_nutrient(food,nutrient":
    food, nutrient =  food_nutrient()
    if sys.argv[1] == "food_nutrient()":
        food, nutreint = eval(sys.argv[1])
        f = open(current_dir + "/search/food_nutrient.txt", 'w', encoding = 'utf8')
        for food_name in food:
            f.write(food_name + '\n')
        for nutrient_name in nutreint:
            f.write(nutrient_name + '\n')
        print("done")
        f.close()
    elif sys.argv[1] in food:
        command = "food_attribute('%s')" %sys.argv[1]
        result = eval(command)
        try:
            f = open(current_dir + "/search/result.txt", 'w', encoding = 'utf8')
            f.write("Tên thực phẩm: " + str(result['label']) + '\n')
            f.write("Loại thực phẩm: " + str(result['type']) + '\n')
            f.write("Calo : " + str(result['Has_calo']) + str("/100g") + '\n')
            f.write("Những chất dinh dưỡng: " + str(", ".join(result['Has_Nutrient'])) + '\n')
            f.write("Thời điểm thích hợp ăn: "+ str(result['Has_suitable_time']) + '\n')
            f.write("Những loại thực phẩm không ăn chung: " + str(", ".join(result['Not_Use_Together'])) + '\n')
            f.write("Cách chế biến: " + str(result['Has_processing']) + '\n')
        except:
            pass

        f.close()
        print("done")
    elif sys.argv[1] in nutrient:
        command = "nutrient_attribute('%s')" %sys.argv[1]
        result = eval(command)
        try:
            f = open(current_dir + "/search/result.txt", 'w', encoding = 'utf8')
            f.write("Tên chất dinh dưỡng: " + str(result['label']) + '\n')
            f.write("Loại chất dinh dưỡng: " + str(result['type']) + '\n')
            f.write("Tác dụng: " + result['Has_effect'] + '\n')
            f.write("Ảnh hưởng khi thừa: " + result['Has_exceed_effect'] + '\n')
            f.write("Ảnh hưởng khi thiếu: "+ result['Has_lack_of_sb_effect'] + '\n')
        except:
            pass

        f.close()
        print("done")
    elif sys.argv[1] == "illness_list()":
        illness_list = eval(sys.argv[1])
        f = open(current_dir + "/search/disease.txt", 'w', encoding = 'utf8')
        for illness_name in illness_list:
            f.write(str(illness_name) + "\n")
        print("done")
        f.close()
    else:
        pass
        # elif sys.argv[1]
    # except:
    #     # print(list_structure_breakfast({"sss": ['Fruits', '43', "['Chanh']", 0]}))
    #     # print(all_food())
    #     print("Your query maybe wrongs")
