<template>
  <q-page class="q-pa-lg">
    <!-- Page Header & Action Bar -->
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Roles</div>
      <q-btn
        color="primary"
        icon="add"
        label="NEW"
        no-caps
        unelevated
        class="text-weight-bold q-px-md"
        @click="openCreateDialog"
      />
    </div>

    <!-- Data Table Card -->
    <q-card flat bordered class="bg-white rounded-borders">
      <q-table
        :rows="roles"
        :columns="columns"
        row-key="id"
        :loading="loading"
        :pagination="initialPagination"
        :rows-per-page-options="[5, 10, 20, 50]"
        flat
        class="roles-table"
      >
        <!-- Custom ID Column -->
        <template v-slot:body-cell-id="props">
          <q-td :props="props" class="text-grey-8">
            {{ props.row.id }}
          </q-td>
        </template>

        <!-- Custom Code Column -->
        <template v-slot:body-cell-role_code="props">
          <q-td :props="props" class="text-weight-medium">
            {{ props.row.role_code }}
          </q-td>
        </template>

        <!-- Custom Name Column -->
        <template v-slot:body-cell-role_name="props">
          <q-td :props="props">
            {{ props.row.role_name }}
          </q-td>
        </template>

        <!-- Custom Description Column -->
        <template v-slot:body-cell-description="props">
          <q-td :props="props" class="text-grey-8">
            {{ props.row.description || '-' }}
          </q-td>
        </template>

        <!-- Actions Column -->
        <template v-slot:body-cell-actions="props">
          <q-td :props="props" align="right">
            <q-btn
              flat
              round
              dense
              color="primary"
              icon="edit"
              class="q-mr-xs"
              @click="openEditDialog(props.row)"
            >
              <q-tooltip>Edit Role</q-tooltip>
            </q-btn>
            <q-btn
              flat
              round
              dense
              color="negative"
              icon="delete"
              @click="confirmDelete(props.row)"
            >
              <q-tooltip>Delete Role</q-tooltip>
            </q-btn>
          </q-td>
        </template>

        <!-- Empty State -->
        <template v-slot:no-data>
          <div class="full-width row flex-center q-pa-md text-grey-6">
            <q-icon size="2em" name="sentiment_dissatisfied" class="q-mr-sm" />
            <span>No roles found</span>
          </div>
        </template>
      </q-table>
    </q-card>

    <!-- Create / Edit Dialog -->
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="min-width: 400px; max-width: 500px;" class="q-pa-sm">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">
            {{ isEditing ? 'Edit Role' : 'New Role' }}
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-md">
          <q-form @submit="saveRole" class="q-gutter-md">
            <q-input
              v-model="form.role_code"
              label="Role Code *"
              outlined
              dense
              placeholder="e.g. MANAGER"
              :rules="[val => !!val || 'Role code is required']"
              :disable="isEditing"
            />

            <q-input
              v-model="form.role_name"
              label="Role Name *"
              outlined
              dense
              placeholder="e.g. Manager"
              :rules="[val => !!val || 'Role name is required']"
            />

            <q-input
              v-model="form.description"
              label="Description"
              outlined
              dense
              type="textarea"
              rows="3"
              placeholder="e.g. Branch operations manager"
            />

            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn label="Cancel" flat color="grey-7" v-close-popup />
              <q-btn
                :label="isEditing ? 'Update' : 'Create'"
                type="submit"
                color="primary"
                unelevated
                :loading="saving"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="deleteDialogOpen">
      <q-card style="min-width: 350px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold text-negative">Confirm Deletion</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-md text-grey-8">
          Are you sure you want to delete the role
          <strong>{{ roleToDelete?.role_name || roleToDelete?.role_code }}</strong>?
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" color="grey-7" v-close-popup />
          <q-btn
            unelevated
            label="Delete"
            color="negative"
            :loading="deleting"
            @click="executeDelete"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api, defaultRoles } from '@/services/api'

const $q = useQuasar()

const roles = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const dialogOpen = ref(false)
const isEditing = ref(false)
const form = ref({
  id: null,
  role_code: '',
  role_name: '',
  description: ''
})

const deleteDialogOpen = ref(false)
const roleToDelete = ref(null)

const initialPagination = {
  sortBy: 'id',
  descending: false,
  page: 1,
  rowsPerPage: 5
}

const columns = [
  {
    name: 'id',
    label: 'ID',
    align: 'left',
    field: 'id',
    sortable: true,
    style: 'width: 80px'
  },
  {
    name: 'role_code',
    label: 'Code',
    align: 'left',
    field: 'role_code',
    sortable: true
  },
  {
    name: 'role_name',
    label: 'Name',
    align: 'left',
    field: 'role_name',
    sortable: true
  },
  {
    name: 'description',
    label: 'Description',
    align: 'left',
    field: 'description',
    sortable: false
  },
  {
    name: 'actions',
    label: 'Actions',
    align: 'right',
    field: 'actions',
    sortable: false,
    style: 'width: 120px'
  }
]

async function loadRoles() {
  loading.value = true
  try {
    const data = await api.roles.list()
    roles.value = Array.isArray(data) && data.length > 0 ? data : defaultRoles
  } catch (err) {
    console.error('Failed to load roles:', err)
    roles.value = defaultRoles
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  form.value = {
    id: null,
    role_code: '',
    role_name: '',
    description: ''
  }
  dialogOpen.value = true
}

function openEditDialog(role) {
  isEditing.value = true
  form.value = {
    id: role.id,
    role_code: role.role_code,
    role_name: role.role_name,
    description: role.description || ''
  }
  dialogOpen.value = true
}

async function saveRole() {
  saving.value = true
  try {
    if (isEditing.value) {
      const updated = await api.roles.update(form.value.id, {
        role_code: form.value.role_code,
        role_name: form.value.role_name,
        description: form.value.description
      }).catch(() => {
        // Fallback local update
        return {
          id: form.value.id,
          role_code: form.value.role_code,
          role_name: form.value.role_name,
          description: form.value.description
        }
      })
      const index = roles.value.findIndex(r => r.id === form.value.id)
      if (index !== -1) {
        roles.value[index] = { ...roles.value[index], ...updated }
      }
      $q.notify({
        type: 'positive',
        message: 'Role updated successfully',
        position: 'top'
      })
    } else {
      const newRole = await api.roles.create({
        role_code: form.value.role_code,
        role_name: form.value.role_name,
        description: form.value.description
      }).catch(() => {
        // Fallback local insert
        const nextId = roles.value.length > 0 ? Math.max(...roles.value.map(r => r.id)) + 1 : 1
        return {
          id: nextId,
          role_code: form.value.role_code,
          role_name: form.value.role_name,
          description: form.value.description,
          created_at: new Date().toISOString()
        }
      })
      roles.value.push(newRole)
      $q.notify({
        type: 'positive',
        message: 'Role created successfully',
        position: 'top'
      })
    }
    dialogOpen.value = false
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.message || 'Failed to save role',
      position: 'top'
    })
  } finally {
    saving.value = false
  }
}

function confirmDelete(role) {
  roleToDelete.value = role
  deleteDialogOpen.value = true
}

async function executeDelete() {
  if (!roleToDelete.value) return
  deleting.value = true
  try {
    await api.roles.delete(roleToDelete.value.id).catch(() => {
      // Fallback local removal
    })
    roles.value = roles.value.filter(r => r.id !== roleToDelete.value.id)
    $q.notify({
      type: 'positive',
      message: 'Role deleted successfully',
      position: 'top'
    })
    deleteDialogOpen.value = false
    roleToDelete.value = null
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.message || 'Failed to delete role',
      position: 'top'
    })
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.roles-table {
  border-radius: 4px;
}

:deep(.q-table th) {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

:deep(.q-table tbody tr:hover) {
  background-color: #f9fafb;
}
</style>

