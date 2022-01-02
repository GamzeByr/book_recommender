import pandas as pd


df_ = pd.read_csv('ratings.csv')
ratings=df_.copy()

df_2 = pd.read_csv('books.csv')
books=df_2.copy()

df=ratings.merge(books[["title","book_id","original_title"]],how="left", on="book_id")
df.head()



#Preparing data
def data_preparing(df):
    df = df[df["book_id"].notna()]
    comment_counts = pd.DataFrame(df["book_id"].value_counts())
    rare_books = comment_counts[comment_counts["book_id"] <=10].index
    common_books = df[~df["book_id"].isin(rare_books)]
    #common_books["rating"].astype(int)
    user_books_df = common_books.pivot_table(index=["user_id"], columns=["book_id"], values="rating")
    return user_books_df, common_books

user_books_df,common_books=data_preparing(df)

#Find read books by user
def read_books(user_books_df, us_id):
    the_user_df = user_books_df[user_books_df.index == us_id]
    read_book = the_user_df.columns[the_user_df.notna().any()].tolist()
    print(read_book)
    return read_book, the_user_df

user_id=12381
read_book,the_user_df=read_books(user_books_df,user_id)
the_user_df.shape


#Find weighted rating for User-Based
def calculating_weighted_rating(user_books_df, read_book, the_user_df, user_id, ratings):
    books_read_df = user_books_df[read_book]
    user_book_count = books_read_df.T.notnull().sum()
    user_book_count = user_book_count.reset_index()
    user_book_count.columns = ["user_id", "book_count"]
    len(read_book)
    users_same_books = user_book_count[user_book_count["book_count"] > 10]["user_id"]

    final_df = pd.concat([books_read_df[books_read_df.index.isin(users_same_books)], the_user_df[read_book]])
    corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
    corr_df = pd.DataFrame(corr_df, columns=["corr"])
    corr_df.index.names = ['user_id_1', 'user_id_2']
    corr_df = corr_df.reset_index()


    top_users = corr_df[(corr_df["user_id_1"] == user_id) & (corr_df["corr"] >= 0.50)][["user_id_2", "corr"]].reset_index(drop=True)
    top_users = top_users.sort_values(by='corr', ascending=False)
    print(top_users.head())
    top_users.rename(columns={"user_id_2": "user_id"}, inplace=True)
    top_users_ratings = top_users.merge(ratings[["user_id", "book_id", "rating"]], how='inner')
    top_users_ratings = top_users_ratings[top_users_ratings["user_id"] != user_id]

    top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating']
    # print(top_users_ratings.head())
    top_users_ratings.groupby('book_id').agg({"weighted_rating": "mean"})
    recommendation_df = top_users_ratings.groupby('book_id').agg({"weighted_rating": "mean"})
    recommendation_df = recommendation_df.reset_index()
    return recommendation_df

recommendation_df=calculating_weighted_rating(user_books_df,read_book,the_user_df,user_id,ratings)

#Recommend 5 books with User_Based
def user_based_reccomendation(recommendation_df, books):
    books_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 3.0].sort_values(
        "weighted_rating", ascending=False)
    final_books_to_be_recommend = books_to_be_recommend.merge(books[["book_id", "title"]])
    final_books_to_be_recommend.drop(columns=["book_id", "weighted_rating"])
    print(final_books_to_be_recommend.head(5))


#Recommend 5 books with Item_Based
def item_based_reccomendation(user_id, user_books_df, df):
    book_id =df[df["user_id"] == user_id].sort_values("rating",ascending=False)["book_id"][0:1].values[0]
    book_id = user_books_df[book_id]
    books_from_item_based = user_books_df.corrwith(book_id).sort_values(ascending=False).head(5)
    print(books_from_item_based[:])

user_based_reccomendation(recommendation_df,books)

item_based_reccomendation(user_id,user_books_df,df)



