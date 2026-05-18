import { useState } from 'react'
import * as Tabs from '@radix-ui/react-tabs'

import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EnhancedDataTable, type Column } from '@/components/ui/EnhancedDataTable'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { useToast } from '@/hooks/useToast'
import { useDepartments, useProgrammes, useSchools, useStreams, useStructureMutations } from '@/hooks/useStructure'
import type { Department, Programme, School, Stream } from '@/types/structure'

const schoolColumns: Column<School>[] = [
  { key: 'code', label: 'Code', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
]

const departmentColumns: Column<Department>[] = [
  { key: 'code', label: 'Code', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'school_name', label: 'School', sortable: true },
]

const programmeColumns: Column<Programme>[] = [
  { key: 'code', label: 'Code', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'department_name', label: 'Department', sortable: true },
  { key: 'level', label: 'Level', filterable: true, filterOptions: [{ label: 'Undergraduate', value: 'UG' }, { label: 'Postgraduate', value: 'PG' }] },
]

const streamColumns: Column<Stream>[] = [
  { key: 'code', label: 'Code', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'programme_name', label: 'Programme', sortable: true },
]

const tabTriggerClass = 'px-4 py-2 text-sm font-semibold transition-colors data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary data-[state=inactive]:text-neutral-500 data-[state=inactive]:hover:text-neutral-700'

export function AcademicStructurePage() {
  const { addToast } = useToast()
  const schools = useSchools()
  const departments = useDepartments()
  const programmes = useProgrammes()
  const streams = useStreams()
  const mutations = useStructureMutations()

  const [schoolForm, setSchoolForm] = useState({ code: '', name: '' })
  const [deptForm, setDeptForm] = useState({ code: '', name: '', school: '' })
  const [progForm, setProgForm] = useState({ code: '', name: '', department: '', level: 'UG', duration_years: 4 })
  const [streamForm, setStreamForm] = useState({ code: '', name: '', programme: '' })

  return (
    <div className="space-y-6">
      <Tabs.Root defaultValue="schools">
        <Tabs.List className="flex border-b border-neutral-200">
          <Tabs.Trigger value="schools" className={tabTriggerClass}>Schools</Tabs.Trigger>
          <Tabs.Trigger value="departments" className={tabTriggerClass}>Departments</Tabs.Trigger>
          <Tabs.Trigger value="programmes" className={tabTriggerClass}>Programmes</Tabs.Trigger>
          <Tabs.Trigger value="streams" className={tabTriggerClass}>Streams</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="schools" className="mt-4 space-y-4">
          <Card>
            <CardTitle>Add School</CardTitle>
            <div className="mt-3 flex flex-wrap items-end gap-3">
              <Input id="school-code" label="Code" value={schoolForm.code} onChange={(e) => setSchoolForm((s) => ({ ...s, code: e.target.value }))} />
              <Input id="school-name" label="Name" value={schoolForm.name} onChange={(e) => setSchoolForm((s) => ({ ...s, name: e.target.value }))} />
              <Button
                loading={mutations.createSchool.isPending}
                onClick={() => mutations.createSchool.mutate(schoolForm, {
                  onSuccess: () => { addToast('School created', undefined, 'success'); setSchoolForm({ code: '', name: '' }) },
                  onError: (err) => addToast('Failed', String(err.message), 'error'),
                })}
              >
                Add
              </Button>
            </div>
          </Card>
          <EnhancedDataTable data={schools.data ?? []} columns={schoolColumns} ariaLabel="Schools" />
        </Tabs.Content>

        <Tabs.Content value="departments" className="mt-4 space-y-4">
          <Card>
            <CardTitle>Add Department</CardTitle>
            <div className="mt-3 flex flex-wrap items-end gap-3">
              <Input id="dept-code" label="Code" value={deptForm.code} onChange={(e) => setDeptForm((s) => ({ ...s, code: e.target.value }))} />
              <Input id="dept-name" label="Name" value={deptForm.name} onChange={(e) => setDeptForm((s) => ({ ...s, name: e.target.value }))} />
              <Select
                id="dept-school"
                label="School"
                value={deptForm.school}
                onValueChange={(school) => setDeptForm((s) => ({ ...s, school }))}
                items={(schools.data ?? []).map((s) => ({ value: s.id, label: s.name }))}
              />
              <Button
                loading={mutations.createDepartment.isPending}
                onClick={() => mutations.createDepartment.mutate(deptForm, {
                  onSuccess: () => { addToast('Department created', undefined, 'success'); setDeptForm({ code: '', name: '', school: '' }) },
                  onError: (err) => addToast('Failed', String(err.message), 'error'),
                })}
              >
                Add
              </Button>
            </div>
          </Card>
          <EnhancedDataTable data={departments.data ?? []} columns={departmentColumns} ariaLabel="Departments" />
        </Tabs.Content>

        <Tabs.Content value="programmes" className="mt-4 space-y-4">
          <Card>
            <CardTitle>Add Programme</CardTitle>
            <div className="mt-3 flex flex-wrap items-end gap-3">
              <Input id="prog-code" label="Code" value={progForm.code} onChange={(e) => setProgForm((s) => ({ ...s, code: e.target.value }))} />
              <Input id="prog-name" label="Name" value={progForm.name} onChange={(e) => setProgForm((s) => ({ ...s, name: e.target.value }))} />
              <Select
                id="prog-dept"
                label="Department"
                value={progForm.department}
                onValueChange={(department) => setProgForm((s) => ({ ...s, department }))}
                items={(departments.data ?? []).map((d) => ({ value: d.id, label: d.name }))}
              />
              <Select
                id="prog-level"
                label="Level"
                value={progForm.level}
                onValueChange={(level) => setProgForm((s) => ({ ...s, level }))}
                items={[{ value: 'UG', label: 'Undergraduate' }, { value: 'PG', label: 'Postgraduate' }]}
              />
              <Button
                loading={mutations.createProgramme.isPending}
                onClick={() => mutations.createProgramme.mutate(progForm, {
                  onSuccess: () => { addToast('Programme created', undefined, 'success'); setProgForm({ code: '', name: '', department: '', level: 'UG', duration_years: 4 }) },
                  onError: (err) => addToast('Failed', String(err.message), 'error'),
                })}
              >
                Add
              </Button>
            </div>
          </Card>
          <EnhancedDataTable data={programmes.data ?? []} columns={programmeColumns} ariaLabel="Programmes" />
        </Tabs.Content>

        <Tabs.Content value="streams" className="mt-4 space-y-4">
          <Card>
            <CardTitle>Add Stream</CardTitle>
            <div className="mt-3 flex flex-wrap items-end gap-3">
              <Input id="stream-code" label="Code" value={streamForm.code} onChange={(e) => setStreamForm((s) => ({ ...s, code: e.target.value }))} />
              <Input id="stream-name" label="Name" value={streamForm.name} onChange={(e) => setStreamForm((s) => ({ ...s, name: e.target.value }))} />
              <Select
                id="stream-prog"
                label="Programme"
                value={streamForm.programme}
                onValueChange={(programme) => setStreamForm((s) => ({ ...s, programme }))}
                items={(programmes.data ?? []).map((p) => ({ value: p.id, label: p.name }))}
              />
              <Button
                loading={mutations.createStream.isPending}
                onClick={() => mutations.createStream.mutate(streamForm, {
                  onSuccess: () => { addToast('Stream created', undefined, 'success'); setStreamForm({ code: '', name: '', programme: '' }) },
                  onError: (err) => addToast('Failed', String(err.message), 'error'),
                })}
              >
                Add
              </Button>
            </div>
          </Card>
          <EnhancedDataTable data={streams.data ?? []} columns={streamColumns} ariaLabel="Streams" />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
