<template>
  <div class="settings-section">
    <div v-if="loadingRoles">Checking permissions...</div>
    <div v-else-if="hasSystemManagerRole">
      <h2>User Extensions</h2>
      <button @click="showAdd = true">Add Extension</button>
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Extension</th>
            <th>Organization ID</th>
            <th>Queue Name</th>
            <th>Join DTMF</th>
            <th>Leave DTMF</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ext in extensions" :key="ext.name">
            <td>{{ ext.user_link }}</td>
            <td>{{ ext.extension }}</td>
            <td>{{ ext.organization_id }}</td>
            <td>{{ ext.queue_name }}</td>
            <td>{{ ext.join_dtmf }}</td>
            <td>{{ ext.leave_dtmf }}</td>
            <td>
              <button @click="editExtension(ext)">Edit</button>
              <button @click="deleteExtension(ext.name)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Add/Edit Modal -->
      <div v-if="showAdd || showEdit" class="modal">
        <form @submit.prevent="showAdd ? addExtension() : updateExtension()">
          <div>
            <label>User</label>
            <input v-model="form.user_link" type="text" required />
          </div>
          <div>
            <label>Extension</label>
            <input v-model="form.extension" type="text" required />
          </div>
          <div>
            <label>Organization ID</label>
            <input v-model="form.organization_id" type="text" />
          </div>
          <div>
            <label>Queue Name</label>
            <input v-model="form.queue_name" type="text" />
          </div>
          <div>
            <label>Join DTMF</label>
            <input v-model="form.join_dtmf" type="text" />
          </div>
          <div>
            <label>Leave DTMF</label>
            <input v-model="form.leave_dtmf" type="text" />
          </div>
          <button type="submit">{{ showAdd ? 'Add' : 'Update' }}</button>
          <button type="button" @click="closeModal">Cancel</button>
          <span v-if="modalError" class="error">{{ modalError }}</span>
        </form>
      </div>
      <span v-if="success" class="success">Success!</span>
      <span v-if="error" class="error">{{ error }}</span>
    </div>
    <div v-else>
      <p>You do not have permission to access this page.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const extensions = ref([])
const form = ref({
  user_link: '',
  extension: '',
  organization_id: '',
  queue_name: '',
  join_dtmf: '',
  leave_dtmf: ''
})
const showAdd = ref(false)
const showEdit = ref(false)
const editName = ref('')
const success = ref(false)
const error = ref('')
const modalError = ref('')

const hasSystemManagerRole = ref(false)
const loadingRoles = ref(true)

async function checkSystemManagerRole() {
  loadingRoles.value = true
  try {
    // Step 1: Get current user
    const userRes = await fetch('/api/method/frappe.auth.get_logged_user')
    const userData = await userRes.json()
    const username = userData.message

    // Step 2: Get user roles
    const rolesRes = await fetch(`/api/resource/User/${username}?fields=["roles"]`)
    const rolesData = await rolesRes.json()
    const roles = (rolesData.data.roles || []).map(r => r.role)

    // Step 3: Check for System Manager
    hasSystemManagerRole.value = roles.includes('System Manager')
  } catch (e) {
    hasSystemManagerRole.value = false
  }
  loadingRoles.value = false
}

async function fetchExtensions() {
  try {
    const res = await fetch('/api/resource/Extensions?limit_page_length=100')
    const data = await res.json()
    extensions.value = data.data
  } catch (e) {
    error.value = 'Failed to load extensions.'
  }
}

function closeModal() {
  showAdd.value = false
  showEdit.value = false
  modalError.value = ''
  form.value = { user_link: '', extension: '', organization_id: '', queue_name: '', join_dtmf: '', leave_dtmf: '' }
}

async function addExtension() {
  try {
    const res = await fetch('/api/resource/Extensions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: form.value })
    })
    if (!res.ok) throw new Error('Add failed')
    success.value = true
    closeModal()
    fetchExtensions()
    setTimeout(() => (success.value = false), 2000)
  } catch (e) {
    modalError.value = 'Failed to add extension.'
  }
}

function editExtension(ext) {
  Object.assign(form.value, ext)
  editName.value = ext.name
  showEdit.value = true
}

async function updateExtension() {
  try {
    const res = await fetch(`/api/resource/Extensions/${editName.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: form.value })
    })
    if (!res.ok) throw new Error('Update failed')
    success.value = true
    closeModal()
    fetchExtensions()
    setTimeout(() => (success.value = false), 2000)
  } catch (e) {
    modalError.value = 'Failed to update extension.'
  }
}

async function deleteExtension(name) {
  if (!confirm('Delete this extension?')) return
  try {
    const res = await fetch(`/api/resource/Extensions/${name}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Delete failed')
    success.value = true
    fetchExtensions()
    setTimeout(() => (success.value = false), 2000)
  } catch (e) {
    error.value = 'Failed to delete extension.'
  }
}

onMounted(async () => {
  await checkSystemManagerRole()
  if (hasSystemManagerRole.value) {
    fetchExtensions()
  }
})
</script>

<style scoped>
.settings-section { margin-bottom: 2rem; }
table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
th, td { border: 1px solid #ccc; padding: 0.5rem; }
.success { color: green; margin-left: 1rem; }
.error { color: red; margin-left: 1rem; }
.modal { background: #fff; border: 1px solid #ccc; padding: 1rem; position: fixed; top: 20%; left: 50%; transform: translate(-50%, 0); z-index: 1000; }
form > div { margin-bottom: 1rem; }
</style> 