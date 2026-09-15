package com.talmale.todo

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

/** A single to-do entry. [id] is stable so list updates animate correctly. */
data class Task(
    val id: Long,
    val title: String,
    val done: Boolean = false
)

/**
 * Stores the task list in SharedPreferences as a small JSON array.
 * Keeps the app dependency-free while surviving restarts.
 */
class TodoRepository(context: Context) {

    private val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun load(): List<Task> {
        val raw = prefs.getString(KEY_TASKS, null) ?: return emptyList()
        return runCatching {
            val array = JSONArray(raw)
            (0 until array.length()).map { i ->
                val obj = array.getJSONObject(i)
                Task(
                    id = obj.getLong("id"),
                    title = obj.getString("title"),
                    done = obj.getBoolean("done")
                )
            }
        }.getOrDefault(emptyList())
    }

    fun save(tasks: List<Task>) {
        val array = JSONArray()
        tasks.forEach { task ->
            array.put(
                JSONObject()
                    .put("id", task.id)
                    .put("title", task.title)
                    .put("done", task.done)
            )
        }
        prefs.edit().putString(KEY_TASKS, array.toString()).apply()
    }

    /** Monotonic id counter, persisted so ids stay unique across restarts. */
    fun nextId(): Long {
        val next = prefs.getLong(KEY_NEXT_ID, 1L)
        prefs.edit().putLong(KEY_NEXT_ID, next + 1).apply()
        return next
    }

    private companion object {
        const val PREFS = "simple_todo"
        const val KEY_TASKS = "tasks"
        const val KEY_NEXT_ID = "next_id"
    }
}
