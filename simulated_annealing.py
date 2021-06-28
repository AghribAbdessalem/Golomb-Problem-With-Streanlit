import time
import random
import math
import golomb as golomb
import streamlit as st
import numpy as np
import pandas as pd
import strings as strings


# -----------------------------------


def objective_function(ruler: list[int]) -> int:
    return ruler[len(ruler) - 1] - ruler[0]


def neighborhood_function(current_ruler: list[int], marks_count: int, max_bound: int, trials_number: int) -> list[int]:
    # try to find best neighbor while trials > 0
    while trials_number > 0:
        random_position = random.randint(1, marks_count - 1)
        random_number = random.randint(1, current_ruler[random_position])


        # create a temp ruler
        temp_ruler = current_ruler.copy()

        temp_ruler[random_position] -= random_number

        temp_ruler.sort()

        # check if golomb ruler (correct ruler)
        if golomb.is_golomb_ruler(temp_ruler):
            return temp_ruler

        trials_number -= 1

    # if fail to find best neighbor, generate a random one
    return golomb.generate_golomb_ruler(marks_count, max_bound, max_generate_time=3600)


def simulated_annealing(marks_count: int, max_bound: int,
                        initial_temperature: float, cooling_coeff: float, computing_time: float,
                        trials_number: int, attempts_in_each_level_of_temperature: int) -> dict:
    # begin time
    start = time.time()
    initial_ruler = golomb.generate_golomb_ruler(marks_count, max_bound, max_generate_time=3600)

    current_ruler = initial_ruler.copy()
    best_ruler = initial_ruler.copy()
    beset_ruler_saved = initial_ruler.copy()

    n = 1  # number of accepted rulers
    i = 1  # iteration number

    best_fitness = objective_function(best_ruler)
    current_temperature = initial_temperature  # current temperature
    # record_best_fitness = []

    # draw line chart
    st.header(strings.simulated_annealing_graph_header)
    df = pd.DataFrame({
        'time': [time.time() - start],
        'Fitness': [best_fitness]
    }).rename(columns={'time': 'index'}).set_index('index')

    chart = st.line_chart(df)

    # stop by computing time
    while time.time() - start < computing_time:
        for j in range(attempts_in_each_level_of_temperature):

            current_ruler = neighborhood_function(current_ruler, marks_count,
                                                  max_bound, trials_number)

            if len(current_ruler) == 0:
                raise ValueError("Fail to find the neighbor ruler")

            current_fitness = objective_function(current_ruler)

            if current_fitness > best_fitness:
                try:
                    p = math.exp((best_fitness - current_fitness) / current_temperature)
                except:
                    pass
                r = random.random()

                # make a decision to accept the worse ruler or not
                if r < p:
                    accept = True  # this worse ruler is accepted
                else:
                    accept = False  # this worse ruler is not accepted
            else:
                accept = True  # accept better ruler
                beset_ruler_saved = current_ruler

            if accept:
                best_ruler = current_ruler  # update the best ruler
                best_fitness = objective_function(best_ruler)
                n = n + 1  # count the rulers accepted

            # draw line chart
            new_df = pd.DataFrame({
                'time': [time.time() - start],
                'Fitness': [best_fitness]
            }).rename(columns={'time': 'index'}).set_index('index')

            chart.add_rows(new_df)

            # end For Loop
        # end For Loop

        i += 1  # increment iterations number
        # record_best_fitness.append(best_fitness)

        # cooling the temperature
        current_temperature = current_temperature * cooling_coeff

        # end time
        end = time.time() - start

    # end While Loop

    # write results
    st.header(strings.results_header)

    col_title, col_value = st.beta_columns([2, 3])

    col_title.write(strings.initial_ruler_msg)
    col_value.markdown(f'<span style="color:#26ba1b">**{str(initial_ruler)}**</span>', unsafe_allow_html=True)

    col_title.write(strings.best_ruler_founded_msg)
    col_value.markdown(f'<span style="color:#26ba1b">**{str(beset_ruler_saved)}**</span>', unsafe_allow_html=True)

    col_title.write(strings.best_fitness_msg)
    col_value.markdown(f'<span style="color:#26ba1b">**{str(beset_ruler_saved[len(beset_ruler_saved)-1])}**</span>', unsafe_allow_html=True)

    col_title.write(strings.run_time_msg)
    col_value.markdown(f'<span style="color:#26ba1b">**{time.time() - start} s**</span>', unsafe_allow_html=True)

    return {"initial_ruler": initial_ruler,
            "best_ruler": beset_ruler_saved,
            "best_fitness": beset_ruler_saved[len(beset_ruler_saved)-1],
            "runtime": end}

