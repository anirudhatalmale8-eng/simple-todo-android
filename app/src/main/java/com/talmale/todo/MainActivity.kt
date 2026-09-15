package com.talmale.todo

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.relocation.BringIntoViewRequester
import androidx.compose.foundation.relocation.bringIntoViewRequester
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.delay

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                TodoScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TodoScreen(viewModel: TodoViewModel = viewModel()) {
    val tasks by viewModel.tasks.collectAsStateWithLifecycle()
    var input by rememberSaveable { mutableStateOf("") }

    // Id of the row currently being edited, plus its in-progress text.
    // Only one row can be open at a time; null means nothing is being edited.
    var editingId by rememberSaveable { mutableStateOf<Long?>(null) }
    var editingText by rememberSaveable { mutableStateOf("") }

    val remaining = remember(tasks) { tasks.count { !it.done } }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Simple To-Do", fontWeight = FontWeight.SemiBold)
                        Text(
                            text = subtitleFor(tasks.size, remaining),
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.testTag("subtitle")
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .imePadding()
                .padding(horizontal = 16.dp)
        ) {
            Spacer(Modifier.height(12.dp))

            AddTaskRow(
                value = input,
                onValueChange = { input = it },
                onSubmit = {
                    viewModel.add(input)
                    input = ""
                }
            )

            Spacer(Modifier.height(12.dp))

            if (tasks.isEmpty()) {
                EmptyState()
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .testTag("task_list"),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = androidx.compose.foundation.layout.PaddingValues(bottom = 24.dp)
                ) {
                    items(tasks, key = { it.id }) { task ->
                        TaskRow(
                            task = task,
                            isEditing = editingId == task.id,
                            editingText = editingText,
                            onEditTextChange = { editingText = it },
                            onStartEdit = {
                                editingId = task.id
                                editingText = task.title
                            },
                            onSaveEdit = {
                                viewModel.rename(task.id, editingText)
                                editingId = null
                            },
                            onCancelEdit = { editingId = null },
                            onToggle = { viewModel.toggle(task.id) },
                            onDelete = { viewModel.delete(task.id) }
                        )
                    }
                }
            }
        }
    }
}

private fun subtitleFor(total: Int, remaining: Int): String = when {
    total == 0 -> "Nothing to do yet"
    remaining == 0 -> "All $total done"
    else -> "$remaining of $total remaining"
}

@Composable
private fun AddTaskRow(
    value: String,
    onValueChange: (String) -> Unit,
    onSubmit: () -> Unit
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier
                .weight(1f)
                .testTag("input"),
            singleLine = true,
            label = { Text("New task") },
            keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(
                imeAction = ImeAction.Done
            ),
            keyboardActions = androidx.compose.foundation.text.KeyboardActions(
                onDone = { onSubmit() }
            )
        )
        Spacer(Modifier.width(8.dp))
        Button(
            onClick = onSubmit,
            enabled = value.isNotBlank(),
            modifier = Modifier.testTag("add_button")
        ) {
            Text("Add")
        }
    }
}

@Composable
private fun EmptyState() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.TopCenter
    ) {
        Text(
            text = "No tasks yet.\nType something above and hit Add.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier
                .padding(top = 48.dp)
                .testTag("empty_state")
        )
    }
}

@Composable
private fun TaskRow(
    task: Task,
    isEditing: Boolean,
    editingText: String,
    onEditTextChange: (String) -> Unit,
    onStartEdit: () -> Unit,
    onSaveEdit: () -> Unit,
    onCancelEdit: () -> Unit,
    onToggle: () -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        if (isEditing) {
            EditTaskRow(
                text = editingText,
                onTextChange = onEditTextChange,
                onSave = onSaveEdit,
                onCancel = onCancelEdit
            )
        } else {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(start = 4.dp, end = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Checkbox(
                    checked = task.done,
                    onCheckedChange = { onToggle() },
                    modifier = Modifier.semantics {
                        contentDescription = "Toggle ${task.title}"
                    }
                )
                Text(
                    text = task.title,
                    modifier = Modifier
                        .weight(1f)
                        .clickable(onClick = onStartEdit)
                        .padding(vertical = 14.dp)
                        .semantics { contentDescription = "Edit ${task.title}" },
                    style = MaterialTheme.typography.bodyLarge,
                    textDecoration = if (task.done) TextDecoration.LineThrough else null,
                    color = if (task.done) {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    }
                )
                TextButton(
                    onClick = onDelete,
                    modifier = Modifier.semantics {
                        contentDescription = "Delete ${task.title}"
                    }
                ) {
                    Text("Delete", color = MaterialTheme.colorScheme.error)
                }
            }
        }
    }
}

/**
 * The same card in edit mode: a focused text field with Save / Cancel beside it.
 * Save is disabled on blank input so a task can't be renamed to nothing.
 *
 * Everything sits on one row on purpose. Stacking the buttons under the field made the
 * card taller than the list viewport once the keyboard was up on a 360x640dp screen,
 * so the buttons got clipped. One row keeps the whole editor about 72dp tall, which
 * fits whatever is left of the screen. It also asks to be scrolled into view, so
 * editing a task low down in the list doesn't open the editor behind the keyboard.
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun EditTaskRow(
    text: String,
    onTextChange: (String) -> Unit,
    onSave: () -> Unit,
    onCancel: () -> Unit
) {
    val focusRequester = remember { FocusRequester() }
    val bringIntoViewRequester = remember { BringIntoViewRequester() }
    // Held locally so the caret can start at the end of the existing title - tapping a
    // task to tack something onto it shouldn't type from position 0.
    var field by remember {
        mutableStateOf(TextFieldValue(text, selection = TextRange(text.length)))
    }
    LaunchedEffect(Unit) {
        focusRequester.requestFocus()
        // The keyboard animates in over a few hundred ms and shrinks the list as it goes,
        // so re-request through the animation rather than guessing when it has settled.
        repeat(5) {
            delay(150)
            bringIntoViewRequester.bringIntoView()
        }
    }

    Row(
        modifier = Modifier
            .bringIntoViewRequester(bringIntoViewRequester)
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        OutlinedTextField(
            value = field,
            onValueChange = {
                field = it
                onTextChange(it.text)
            },
            modifier = Modifier
                .weight(1f)
                .focusRequester(focusRequester)
                .testTag("edit_input"),
            singleLine = true,
            label = { Text("Edit task") },
            keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(
                imeAction = ImeAction.Done
            ),
            keyboardActions = androidx.compose.foundation.text.KeyboardActions(
                onDone = { if (text.isNotBlank()) onSave() }
            )
        )
        Spacer(Modifier.width(4.dp))
        TextButton(
            onClick = onCancel,
            contentPadding = PaddingValues(horizontal = 8.dp),
            modifier = Modifier.semantics { contentDescription = "Cancel edit" }
        ) {
            Text("Cancel")
        }
        Button(
            onClick = onSave,
            enabled = text.isNotBlank(),
            contentPadding = PaddingValues(horizontal = 12.dp),
            modifier = Modifier.semantics { contentDescription = "Save edit" }
        ) {
            Text("Save")
        }
    }
}
