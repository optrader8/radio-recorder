import { createFileRoute } from '@tanstack/react-router'

function DashboardPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Active Recordings</h3>
          <p className="text-2xl font-bold text-gray-900">0</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Total Recordings</h3>
          <p className="text-2xl font-bold text-gray-900">0</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Scheduled Jobs</h3>
          <p className="text-2xl font-bold text-gray-900">0</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Storage Used</h3>
          <p className="text-2xl font-bold text-gray-900">0 GB</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Recordings</h2>
          <p className="text-gray-500">No recordings yet. Start your first recording to see it here.</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>API Status</span>
              <span className="text-green-600">Healthy</span>
            </div>
            <div className="flex justify-between">
              <span>Database</span>
              <span className="text-green-600">Connected</span>
            </div>
            <div className="flex justify-between">
              <span>Redis</span>
              <span className="text-green-600">Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage