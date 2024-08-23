# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie: ')
st.write('The name of your Smoothie will be', name_on_order)

# session = get_active_session()
cnx = st.connection('snowflake')
session = cnx.session()

my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'), col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)

pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)

ingredients_list = st.multiselect(
    'Choose upto 5 ingredients:',
    my_dataframe, 
    max_selections=5
)

ingredients_string = ''

if ingredients_list:

    fruits_list = []

    for fruit in ingredients_list:
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit,' is ', search_on, '.')
        st.subheader(fruit + 'Nutritional Information')
        fruits_list.append(search_on)
            
        get_url = f"https://www.fruityvice.com/api/fruit/{search_on}"
        fruityvice_response = requests.get(get_url)
        st.text(get_url)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)


    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    
    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit order')

    if time_to_insert and ingredients_string:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!' + name_on_order, icon="✅")
