import sys
import math
import heapq 

# Dictionary of movies with key = movie; value = list of users rated for the movie
users_rate_movie_dict= {}

# Dictionary of user with key = user; value = list of movies
movies_rated_by_user_dict = {}

# Dictionary of rating with key = (movieID, userID); value = rating
rating_dict = {}

def read_from_file(fn):

    global users_rate_movie_dict
    global rating_dict
    global movies_rated_by_user_dict

    with open(fn) as f:
        content = f.readlines()
    
    for line in content:
        movie_user_rating =  line.rstrip('\n').split(",")
        movie = int(movie_user_rating[0])
        user = int(movie_user_rating[1])
        rating = float(movie_user_rating[2])
        
        if movie not in users_rate_movie_dict:
            users_rate_movie_dict[movie] = [user]
        else:
            users_rate_movie_dict[movie].append(user)

        if user not in movies_rated_by_user_dict:
            movies_rated_by_user_dict[user] = [movie]
        else:
            movies_rated_by_user_dict[user].append(movie)

        rating_dict[(movie,user)] = rating

def find_neighbors(k,movie_i):
    
    similarity = {} # key = movie_j, value = weight_ij

    users_rate_for_i = users_rate_movie_dict[movie_i]
    #print(users_rate_for_i)

    # Find all rating for movie i:
    all_rating_for_i ={}
    for user in users_rate_for_i:
        all_rating_for_i[user] = rating_dict[(movie_i,user)]
    
    # Calculate mean of all rating for movie_i
    rating_i_list= [rating for rating in all_rating_for_i.values()]
    mean_rating_i = sum(rating_i_list)/len(rating_i_list)

    # rating deviation of each user toward movie_i
    deviation_i = {}
    for user in users_rate_for_i:
        deviation_i[user] = rating_dict[(movie_i,user)] - mean_rating_i
    #print(deviation_i)

    # Calculation of part1 of denominator
    deviation_i_list = [dev for dev in deviation_i.values()]
    sum_1 = 0
    for i in deviation_i_list:
        sum_1 += i*i

    ### Compute correlation between rows
    for movie_j in users_rate_movie_dict: 
        if movie_i != movie_j:
            users_rate_for_j = users_rate_movie_dict[movie_j]
            users_rate_both_ij = list(set(users_rate_for_i).intersection(users_rate_for_j))
            #print(users_rate_both_ij)
            if len(users_rate_both_ij)>0:
                
                #all rating for j
                all_rating_for_j ={}
                for user in users_rate_for_j:
                    all_rating_for_j[user] = rating_dict[(movie_j,user)]
                #calculate mean & deviation of movie_j
                rating_j_list= [rating for rating in all_rating_for_j.values()]
                mean_rating_j = sum(rating_j_list)/len(rating_j_list)
                deviation_j = {}
                for user in users_rate_for_j:
                    deviation_j[user] = rating_dict[(movie_j,user)] - mean_rating_j

                # Calculation of part2 of denominator
                deviation_j_list = [dev for dev in deviation_j.values()]
                sum_2 = 0
                for i in deviation_j_list:
                    sum_2 += i*i
                 
                numerator = sum(deviation_i[m]*deviation_j[m] for m in users_rate_both_ij)
                denominator = math.sqrt(sum_1)* math.sqrt(sum_2)

                weigh_ij = numerator/denominator
                #print(weigh_ij)

                similarity[movie_j] = weigh_ij
                
                # Find K nearest neighbors
                if k <= len(similarity):
                    neighbors = {key: value for key, value in similarity.items() if value in heapq.nlargest(k, similarity.values())}

                else:
                    neighbors = {key: value for key, value in similarity.items() if value in heapq.nlargest(len(similarity), similarity.values())}
    
    return neighbors 	# key = movie_j, value = weight_ij
    
def prediction(neighbors,user,movie_i):
    numerator = 0
    denominator = 0
    for movie,weight in neighbors.items():
        if (movie,user) in rating_dict:
            numerator += weight * rating_dict[(movie,user)]
            #print(rating_dict[(movie,user)])
            denominator += weight
            #print(a)
            #print(numerator)
            #print(denominator)
    if denominator == 0:
        users_rate_for_i = users_rate_movie_dict[movie_i]
        all_rating_for_i = { user:rating_dict[(movie_i,user)] for user in users_rate_for_i }
        rating_i_list= [rating for rating in all_rating_for_i.values()]
        predict = sum(rating_i_list)/len(rating_i_list)

    else: 
        predict = numerator/denominator
    predict = min(5.0, predict)
    predict = max(0.0,predict)
    return predict

def prediction_input():
    good_input = True
    while good_input:
        try:
            user_id = int(input("Enter User ID: "))
            movie_id = int(input("Enter movie ID: "))
            k = int(input("Enter an integer for k: "))
            if movie_id in users_rate_movie_dict and user_id in movies_rated_by_user_dict:
                return user_id, movie_id, k
            else:
                print("Please only enter existing movie_id and user_id in data file! ")
        except ValueError:
            print("Error! please enter integer only.")

if __name__ == '__main__':
    infile = sys.argv[1]
    read_from_file(infile)
    
    user_id, movie_id, k = prediction_input()

    neighbors = find_neighbors(k,movie_id)
    
    prediction = prediction(neighbors,user_id,movie_id)
    print("Predict: the user %d will rate %3.1f for the movie %d" % (user_id,prediction,movie_id))
    if prediction >= 2.5:
        print("RECOMMEND!")
    else:
        print("Do not recommend!")



    
 
