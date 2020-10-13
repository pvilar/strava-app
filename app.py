import os
import re
import logging

# import plotly.express as px
import streamlit as st

from pystrava.utils import get_first_time_token, refresh_access_token_if_expired  # noqa: E501
from pystrava.segments import sort_segments_from_activity, format_segments_table  # noqa: E501
from pystrava.transformations import get_segment_coordinates, get_activity_coordinates  # noqa: E501
from pystrava.maps import create_map


def main():
    # Display title and any other information at the top
    st.title("SegmentBreaker")
    st.markdown("## Be The Next Strava Leader")

    # Link to app's OAuth Authorization page
    st.markdown(
        "Click on the following link in order to authorise SegmentBreaker to connect to your Strava"  # noqa: E501
    )
    url_oauth = 'https://www.strava.com/oauth/authorize?client_id=%2053827&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all'  # noqa: E501
    st.markdown(url_oauth)

    # Text box to input URL from auth
    oauth_response = st.text_input(
        "Enter the URL you got after authorizing the app to access your training data"  # noqa: E501
    )
    if not oauth_response:
        st.warning('Please input the URL you got after authorizing the app')
    else:
        CODE = re.search('code=(.*)&', oauth_response).group(1)

        # TODO: select activity from date?
        # get activity id from user input
        ACTIVITY_ID = st.text_input(
            "Enter an activity id from your trainings"
        )  # ,'4074378152')  # remove default activity id in production

        if not ACTIVITY_ID:
            st.warning('Please input a valid activity id from your profile')
            # st.stop()
        else:
            # TODO: Check if activity id is valid (trying to pull data
            # from the activity id)
            try:
                # Refresh tokens if expired or don't have tokens yet
                tokens = call_refresh_access_token_if_expired(tokens)
                logger.info("Refreshing tokens if necessary")
            except NameError:
                # get tokens
                tokens = call_get_first_time_token(
                    CODE)  # only need to call this once!

            # display map from activity
            df_activity_coordinates = get_activity_coordinates(
                ACTIVITY_ID, tokens)
            st.header("Activity map")
            # st.map(df_activity_coordinates)
            activity_map = create_map(df_activity_coordinates, 'dark')
            st.pydeck_chart(activity_map)

            # returns the sorted segments by time delta
            df_segments = call_segments_sorting(ACTIVITY_ID, tokens)
            df_segments_formatted = format_segments_table(df_segments)

            # TODO: format segments dataframe to show only valuable information
            # displays the segments dataframe with a checkbox to select on the
            # distance of the segment
            st.header("Ranked segments by proximity to Strava leader")
            # distance = st.selectbox(
            #     "Get segments above certain distance in KM:",
            #     range(0, int(max(df_segments['distance']))))
            # df_segments_filtered = df_segments[df_segments['distance'] >= distance]
            # df_segments_filtered = df_segments
            st.write(df_segments_formatted)

            # select segment to analyse
            segment_name = st.selectbox("Select a segment to visualize",
                                        df_segments["name"].unique())

            # get segment id from name
            segment_id = df_segments.loc[df_segments['name'] == segment_name,
                                         'segment.id'].values[0]

            # display segment map
            df_segment_coordinates = get_segment_coordinates(
                str(segment_id), tokens)
            st.header("Segment map")
            # st.map(df_segment_coordinates)
            segment_map = create_map(df_segment_coordinates, 'outdoors')
            st.pydeck_chart(segment_map)


@st.cache
def call_get_first_time_token(CODE):
    return get_first_time_token(CODE)


@st.cache
def call_refresh_access_token_if_expired(tokens):
    return refresh_access_token_if_expired(tokens)


# This functions calls the function that sorts the segments from the pystrava
# module. In order to apply the cache option, the function that loads the data
# needs to be defined in this script (so it's a workaround to use sort_segments_from_activity() cached  # noqa: E302, E501
@st.cache
def call_segments_sorting(ACTIVITY_ID, tokens):
    return sort_segments_from_activity(activity_id=ACTIVITY_ID,
                                       gender=GENDER,
                                       tokens=tokens)


# General parameters
# ACTIVITY_ID = '4074378152'
GENDER = 'man'
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

logger = logging.getLogger("pystrava")

if __name__ == "__main__":
    main()
