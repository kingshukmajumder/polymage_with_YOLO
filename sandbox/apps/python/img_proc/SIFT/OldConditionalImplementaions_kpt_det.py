# Siddharth's Pyhton Implementation 

# def create_comparing_rect(current, relation, compare_to, xvar, yvar):
#     indeces = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
#     conds = []

#     for (xcoeff, ycoeff) in indices:
#         if xcoeff == 0 && ycoeff == 0:
#             continue
#         cond = Condition((current(x, y)), relation, compare_to(xvar - xcoeff, yvar - ycoeff))

#     final_cond = conds[0]
#     for cond in conds[1:]:
#         final_cond = final_cond & cond

#     return final_cond

# (create_comparing_rect(current, '>=', high, x, y) &
# create_comparing_rect(current, '>=', current, x, y) &
# create_comparing_rect(current, '>=', low, x, y)) | 
# (create_comparing_rect(current, '<=', high, x, y) &
# create_comparing_rect(current, '<=', current, x, y) &
# create_comparing_rect(current, '<=', low, x, y))

# My Rolled out Conditional Statement 

# # Set of conditions that I want to convert into a condition 
# # stencil 
# cond = (Condition(current(x,y) '>=' high(x-1,y-1)) & \
#             Condition(current(x,y) '>=' high(x,y-1)) & \
#             Condition(current(x,y) '>=' high(x+1,y-1)) & \
#             Condition(current(x,y) '>=' high(x-1,y)) & \
#             Condition(current(x,y) '>=' high(x,y)) & \
#             Condition(current(x,y) '>=' high(x+1,y)) & \
#             Condition(current(x,y) '>=' high(x-1,y+1)) & \
#             Condition(current(x,y) '>=' high(x,y+1)) & \
#             Condition(current(x,y) '>=' high(x+1,y+1)) & \
#             Condition(current(x,y) '>=' current(x-1,y-1)) & \
#             Condition(current(x,y) '>=' current(x,y-1)) & \
#             Condition(current(x,y) '>=' current(x+1,y-1)) & 
#             Condition(current(x,y) '>=' current(x-1,y)) & \
#             Condition(current(x,y) '>=' current(x+1,y)) & \
#             Condition(current(x,y) '>=' current(x-1,y+1)) & \
#             Condition(current(x,y) '>=' current(x,y+1)) \
#             Condition(current(x,y) '>=' current(x+1,y+1)) \
#             Condition(current(x,y) '>=' low(x-1,y-1)) & \
#             Condition(current(x,y) '>=' low(x,y-1)) & \
#             Condition(current(x,y) '>=' low(x+1,y-1)) & \
#             Condition(current(x,y) '>=' low(x-1,y)) & \
#             Condition(current(x,y) '>=' low(x,y)) & \
#             Condition(current(x,y) '>=' low(x+1,y)) &\
#             Condition(current(x,y) '>=' low(x-1,y+1)) & \
#             Condition(current(x,y) '>=' low(x,y+1)) & \
#             Condition(current(x,y) '>=' low(x+1,y+1)) ) | \
#         (Condition(current(x,y) '<=' high(x-1,y-1)) & \
#             Condition(current(x,y) '<=' high(x,y-1)) & \
#             Condition(current(x,y) '<=' high(x+1,y-1)) & \
#             Condition(current(x,y) '<=' high(x-1,y)) & \
#             Condition(current(x,y) '<=' high(x,y)) & \
#             Condition(current(x,y) '<=' high(x+1,y)) & \
#             Condition(current(x,y) '<=' high(x-1,y+1)) & \
#             Condition(current(x,y) '<=' high(x,y+1)) & \
#             Condition(current(x,y) '<=' high(x+1,y+1)) & \
#             Condition(current(x,y) '<=' current(x-1,y-1)) & \
#             Condition(current(x,y) '<=' current(x,y-1)) & \
#             Condition(current(x,y) '<=' current(x+1,y-1)) & \
#             Condition(current(x,y) '<=' current(x-1,y)) & \
#             Condition(current(x,y) '<=' current(x+1,y)) & \
#             Condition(current(x,y) '<=' current(x-1,y+1)) & \
#             Condition(current(x,y) '<=' current(x,y+1)) & \
#             Condition(current(x,y) '<=' current(x+1,y+1)) & \
#             Condition(current(x,y) '<=' low(x-1,y-1)) & \
#             Condition(current(x,y) '<=' low(x,y-1)) &\
#             Condition(current(x,y) '<=' low(x+1,y-1)) & \
#             Condition(current(x,y) '<=' low(x-1,y)) & \
#             Condition(current(x,y) '<=' low(x,y)) & \
#             Condition(current(x,y) '<=' low(x+1,y)) & \
#             Condition(current(x,y) '<=' low(x-1,y+1)) & \
#             Condition(current(x,y) '<=' low(x,y+1)) & \
#             Condition(current(x,y) '<=' low(x+1,y+1)) )