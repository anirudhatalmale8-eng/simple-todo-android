package com.talmale.todo

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class TodoViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = TodoRepository(application)

    private val _tasks = MutableStateFlow(repository.load())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    /** Ignores blank input so the Add button can't create empty rows. */
    fun add(title: String) {
        val trimmed = title.trim()
        if (trimmed.isEmpty()) return
        update(_tasks.value + Task(id = repository.nextId(), title = trimmed))
    }

    /** Renames a task in place. Blank input is ignored, same as [add]. */
    fun rename(id: Long, title: String) {
        val trimmed = title.trim()
        if (trimmed.isEmpty()) return
        update(_tasks.value.map { if (it.id == id) it.copy(title = trimmed) else it })
    }

    fun toggle(id: Long) {
        update(_tasks.value.map { if (it.id == id) it.copy(done = !it.done) else it })
    }

    fun delete(id: Long) {
        update(_tasks.value.filterNot { it.id == id })
    }

    private fun update(tasks: List<Task>) {
        _tasks.value = tasks
        repository.save(tasks)
    }
}
