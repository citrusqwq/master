package com.example.peekareadapp

import android.graphics.Rect
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class ScanScreenViewModel: ViewModel() {
    private val _state = MutableStateFlow(ScanScreenState())
    val state = _state.asStateFlow()

    // mutable state variable to keep track of selected blocks
    private val _selectedBlocks = MutableStateFlow<List<Rect>>(emptyList())
    val selectedBlocks: StateFlow<List<Rect>> = _selectedBlocks
    fun selectBlock(block: Rect) {
        _selectedBlocks.value = _selectedBlocks.value + block
    }
}

class ScanScreenState