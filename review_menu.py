from function_file import *
from query_rdfs import *
import json
import sys
import os
from operator import itemgetter
import itertools
import random

sys.path.append(os.path.join(os.path.dirname("__file__"), '..'))
current_dir = os.path.dirname("__file__")
current_dir = current_dir if current_dir is not '' else '.'
# directory to scan for any txt files
data_dir_path = current_dir + '/menu_review'
known_dir_path = current_dir + '/Information_user'
rule_dir_path = current_dir + "/rule"


with open(data_dir_path + "/menu.json", 'r', encoding='utf8') as lst:
    data = json.load(lst)
with open(known_dir_path + "/known.json", 'r', encoding='utf8') as lst:
    known = json.load(lst)
known["BreakFast"] = data["Has_Breakfast"]
known["Lunch"] = data["Has_Lunch"]
known["Dinner"] = data["Has_Dinner"]

data_rule = []
function = []

with open(rule_dir_path + "/rule_review.txt", "r", encoding="utf8") as f:
    for line in f:
        data_rule.append(line)
with open(rule_dir_path + "/function.txt", "r", encoding="utf8") as f:
    for line in f:
        function.append(line)


def list_food_create(list_need_food, list_limit_food,
                     list_avoid_food, list_unlike_food):
    result = {}
    list_all_food = []
    tamp_list = [food.split("|") for food in all_food()]
    set_avoid_food = set(list_avoid_food)
    for item in list_unlike_food:
        set_avoid_food.add(item)
    for food in tamp_list:
        list_all_food.append(food)
    for food in list_all_food:
        if food[0] in list_need_food:
            food.append(2)
            result[food[0]] = food[1:]
        elif food[0] in list_limit_food:
            food.append(0)
            result[food[0]] = food[1:]
        elif food[0] in set_avoid_food:
            food.append(-1)
            result[food[0]] = food[1:]
        else:
            food.append(1)
            result[food[0]] = food[1:]
    return result

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def BMIvalueCalc(height, weight):
    height /= 100
    return round(eval(function[2].split("=")[1]), 2)


def BMIrangeCalc(bmi_value):
    return BMI_range_calc(bmi_value)


def BMIlevelCalc(bmi_range):
    return has_value(bmi_range)["value"]
#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def BMRvalueOfMaleCalc(height, weight, age):
    result = function[1].split("=")[1]
    return round(eval(result), 2)


def BMRvalueOfFemaleCalc(height, weight, age):
    result = function[0].split("=")[1]
    return round(eval(result), 2)

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def PAvalueCalc(PhysicalActiveLevel):
    for count in range(4, 9):
        result = function[count].split(":")
        if result[1].endswith("\n"):
            result[1] = result[1][:-1]
        if result[1] == PhysicalActiveLevel:
            return float(result[0])

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def CaloCalc(BMRvalue, PhysicalActiveValue, target):
    result = round(eval(function[3].split("=")[1]), 2)

    if target == "tăng cân":
        result += 500
    elif target == "giảm cân":
        result -= 500
    return result

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def CaloToKeepWeightCalc(calo_per_day):
    # breakfast: 26%, #Lunch: 40%, # Dinner: 34%
    return [round(calo_per_day*26/100, 2),
            round(calo_per_day*40/100, 2), round(calo_per_day*34/100, 2)]


def CaloToGainWeightCalc(calo_per_day):
    # breakfast: 26%, #Lunch: 40%, # Dinner: 34%
    return [round(calo_per_day*26/100, 2),
            round(calo_per_day*40/100, 2), round(calo_per_day*34/100, 2)]


def CaloToLoseWeightCalc(calo_per_day):
    # breakfast: 26%, #Lunch: 40%, # Dinner: 34%
    return [round(calo_per_day*26/100, 2),
            round(calo_per_day*40/100, 2), round(calo_per_day*34/100, 2)]

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def FindAvoidFood(list_illness):
    return avoided_group_food(list_illness)  # return array


def FindNeedFood(list_illness):
    return needed_group_food(list_illness)


def FindLimitFood(list_illness):
    return limit_food(list_illness)


#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def extract_rule_left(rule_left):
    rule_left = re.findall(r'\[(.*?)\]', rule_left)
    flag = True
    for content in rule_left:
        content = content.split(",")
        if content[0] == "1":
            if content[1] not in known:
                flag = False
                break
        elif content[0] == "2":
            try:
                if known[content[1]] != content[2]:
                    flag = False
                    break
            except:
                flag = False
                break
    return flag


def extract_rule_right(rule_right):
    rule_right = rule_right.split(",", 1)
    flag = True
    rule_right[0] = rule_right[0][1:]
    rule_right[1] = rule_right[1][:-2]
    if rule_right[0] in known:
        flag = False
    else:
        funct = rule_right[1].split(':')[1]
        known[rule_right[0]] = eval(funct)
    return flag


def extract_rule(rule):
    flag = True
    # print(rule)
    rule_left, rule_right = rule.split("|")
    flag = extract_rule_left(rule_left)
    if flag is False:
        return flag
    else:
        flag = extract_rule_right(rule_right)
    return flag

#
# ─── --- ────────────────────────────────────────────────────────────────────────
#


def JoinFood(breakfast, lunch, dinner):
    food = (breakfast, lunch, dinner)
    return food


def list_food_not_use_together(list_food, meal):
    result = set()
    list_food_name = []
    list_food_not_use = {}

    for food_name in meal:
        list_food_name.append(food_name[0])
        food_not_use = re.findall(r'\[(.*?)\]', list_food[food_name[0]][2])
        if food_not_use != []:
            list_food_not_use[food_name[0]] = []
            food_not_use = food_not_use[0].split(",")
            food_not_use = list(
                map(lambda x: x.replace("'", ""), food_not_use))
            for item in food_not_use:
                list_food_not_use[food_name[0]].append(item)
    for food in list_food_name:
        for key in list_food_not_use:
            for value in list_food_not_use[key]:
                if value == food:
                    temp = "%s - %s" % (value, key)
                    result.add(temp)
    return result


def caculate_calo(menu):
    result = 0
    for meal in menu:
        for food in meal:
            result += food[1]

    return result


def portion_meal(menu, calo_menu):
    result = []
    for meal in menu:
        meal_calo = 0
        for food in meal:
            meal_calo += food[1]
        tamp = round(meal_calo / calo_menu * 100, 2)
        result.append(tamp)

    return result


def condittion_percetage(portion):
    one = portion[0]
    two = portion[1]
    three = portion[2]
    if one in range(22, 30+1) and two in range(35, 45+1) and three in range(30, 38+1):
        return True
    return False


def caculate_menu_score_review(menu, list_food):
    score_real = 0
    score_abstract = 0
    confident = None
    ideal_score = 2
    for meal in menu:
        for food in meal:
            score_real += list_food[food[0]][3]  # food_score
            score_abstract += ideal_score

    confident = round(score_real / score_abstract * 100, 2)
    return confident


def main():
    # f = open(data_dir_path + "id_menu.txt", 'r')
    food_not_use_together = set()

    count = 0
    while count <= 13:
        # print(data_rule[count])
        if extract_rule(data_rule[count]) == True:
            # print("True")
            count = 0
            continue
        else:
            # print(extract_rule(data_rule[count]))
            count += 1
    list_food = list_food_create(known["ListNeedFood"], known["ListNeedFood"],
                                 known["ListAvoidFood"], known["UnLikeFood"])
    menu_score = caculate_menu_score_review(known["RealListFood"], list_food)
    calo_real = caculate_calo(known["RealListFood"])
    percetage_real = portion_meal(known["RealListFood"], calo_real)
    percetage_real = [str(item)+"%" for item in percetage_real]
    calor_difference = round(calo_real - known["CaloPerDay"], 2)
    menu_score = round(menu_score - abs(calor_difference)/100, 0)


    if condittion_percetage(percetage_real):
        flag = True
    else:
        flag = False

    for meal in known["RealListFood"]:
        if list_food_not_use_together(list_food, meal) != set():
            for item in list_food_not_use_together(list_food, meal):
                food_not_use_together.add(item)

    f = open(data_dir_path + "/result_review.txt", "w", encoding="utf8")

    f.write("Tổng lượng calo của thực đơn: " + str(calo_real) + '\n')
    f.write("Lượng calo cần cung cấp theo thể trạng: " +
            str(known["CaloPerDay"]) + '\n')
    f.write("Lượng calo chêch lệch: " + str(calor_difference) + '\n')
    f.write("Tỉ lệ cho 3 bữa: " + " ".join(percetage_real) + '\n')
    if flag == False:
        f.write("Đề xuất: Bữa sáng : 22-30%, Bữa trưa: 35-45%, Bữa tối: 30-38%" + '\n')
    f.write("Cặp thực phẩm không dùng chung: " +
            ", ".join(food_not_use_together) + '\n')
    f.write("Thực phẩm nên tránh: " + ", ".join(known["ListAvoidFood"]) + '\n')
    f.write("Thực phẩm nên ăn: " + ", ".join(known["ListNeedFood"]) + '\n')
    f.write("Thực phẩm cần hạn chế: " +
            ", ".join(known["ListLimitFood"]) + '\n')
    f.write("Điểm thực đơn: : " + str(menu_score) + '/100')
    print("done")
    f.close()


if __name__ == "__main__":
    main()
