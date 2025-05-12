<template>
  <div class="settings-section">
    <div v-if="loadingRoles">Checking permissions...</div>
    <div v-else-if="hasSystemManagerRole">
      <h2>Telephony/Provider Global Settings</h2>
      <div v-if="!editing">
        <div><strong>Customer ID:</strong> {{ form.organization_id }}</div>
        <div><strong>API Key:</strong> {{ form.api_key }}</div>
        <div><strong>Check Contacts Info From:</strong> {{ form.check_contacts_info_from }}</div>
        <div><strong>Open File:</strong> {{ form.open_file }}</div>
        <div><strong>Incoming Ringtone:</strong> {{ form.incoming_ringtone }}</div>
        <button @click="openModal">Edit</button>
        <span v-if="success" class="success">Saved!</span>
        <span v-if="error" class="error">{{ error }}</span>
      </div>
      <div v-if="editing" class="modal">
        <form @submit.prevent="saveSettings">
          <div>
            <label>Customer ID</label>
            <input v-model="editForm.organization_id" type="text" />
          </div>
          <div>
            <label>API Key</label>
            <input v-model="editForm.api_key" type="text" />
          </div>
          <div>
            <label>Check Contacts Info From</label>
            <input v-model="editForm.check_contacts_info_from" type="text" />
          </div>
          <div>
            <label>Open File</label>
            <input v-model="editForm.open_file" type="text" />
          </div>
          <div>
            <label>Incoming Ringtone (.mp3)</label>
            <input v-model="editForm.incoming_ringtone" type="text" />
          </div>
          <button type="submit">Save</button>
          <button type="button" @click="closeModal">Cancel</button>
          <span v-if="modalError" class="error">{{ modalError }}</span>
        </form>
      </div>
    </div>
    <div v-else>
      <p>You do not have permission to access this page.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const form = ref({
  organization_id: '',
  api_key: '',
  check_contacts_info_from: '',
  open_file: '',
  incoming_ringtone: ''
})
const editForm = ref({ ...form.value })
const editing = ref(false)
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

async function fetchSettings() {
  try {
    const res = await fetch('/api/resource/Global Settings/Global Settings')
    const data = await res.json()
    Object.assign(form.value, data.data)
  } catch (e) {
    error.value = 'Failed to load settings.'
  }
}

function openModal() {
  Object.assign(editForm.value, form.value)
  editing.value = true
  modalError.value = ''
}

function closeModal() {
  editing.value = false
  modalError.value = ''
}

async function saveSettings() {
  try {
    const res = await fetch('/api/resource/Global Settings/Global Settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: editForm.value })
    })
    if (!res.ok) throw new Error('Save failed')
    Object.assign(form.value, editForm.value)
    success.value = true
    error.value = ''
    closeModal()
    setTimeout(() => (success.value = false), 2000)
  } catch (e) {
    modalError.value = 'Failed to save settings.'
  }
}

onMounted(async () => {
  await checkSystemManagerRole()
  if (hasSystemManagerRole.value) {
    fetchSettings()
  }
})
</script>

<style scoped>
.settings-section { margin-bottom: 2rem; }
.success { color: green; margin-left: 1rem; }
.error { color: red; margin-left: 1rem; }
form > div { margin-bottom: 1rem; }
.modal { background: #fff; border: 1px solid #ccc; padding: 1rem; position: fixed; top: 20%; left: 50%; transform: translate(-50%, 0); z-index: 1000; }
</style> 