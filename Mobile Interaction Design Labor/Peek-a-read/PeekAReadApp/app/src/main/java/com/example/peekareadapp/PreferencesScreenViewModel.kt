package com.example.peekareadapp

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
class PreferencesScreenViewModel: ViewModel() {

    private val _state = MutableStateFlow(PreferencesScreenState())
    val state = _state.asStateFlow()
}

class PreferencesScreenState