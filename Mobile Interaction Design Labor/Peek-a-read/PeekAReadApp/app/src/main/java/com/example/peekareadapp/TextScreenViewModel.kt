package com.example.peekareadapp

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
class TextScreenViewModel: ViewModel() {

    private val _state = MutableStateFlow(TextScreenState())
    val state = _state.asStateFlow()
}

class TextScreenState