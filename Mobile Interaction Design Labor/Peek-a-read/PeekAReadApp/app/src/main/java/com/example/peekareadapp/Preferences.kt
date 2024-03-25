package com.example.peekareadapp

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

/**
 * View Model for the user's preferences.
 */
class Preferences : ViewModel() {
    private val _Preferences = MutableLiveData<Preferences>()
    val Preferences: LiveData<Preferences> get() = _Preferences

    // This represents the desired text colour of the displayed text.
    // Probably has to be changed when implemented properly.
    var desired_text_colour: String? = null

    // This represents the desired background colour of the displayed text.
    // Probably has to be changed when implemented properly.
    var desired_background_colour: String? = null

    // This represents the desired font of the displayed text.
    // Probably has to be changed when implemented properly.
    var desired_font: String? = null


    // Function to update user's preferences
    // Probably has to be changed when implemented properly.
    fun updatePreferences(text_colour: String, background_colour: String, font: String) {
        desired_text_colour = text_colour
        desired_background_colour = background_colour
        desired_font = font

        // Notify observers with the updated user data
        _Preferences.value = this
    }
}