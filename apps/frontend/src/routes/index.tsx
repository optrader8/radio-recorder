import { Link } from '@tanstack/react-router'

function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          Radio Recorder
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600">
          A headless radio recording system with web dashboard.
          Automatically record internet radio streams and manage your recordings.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link
            to="/dashboard"
            className="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Get started
          </Link>
          <a href="/api/v1/docs" className="text-sm font-semibold leading-6 text-gray-900">
            API Documentation <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>

      <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
        <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-2 lg:gap-y-16">
          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-gray-900">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.443 1.667-.986l11.54 7.058a1.125 1.125 0 010 1.942l-11.54 7.058a1.125 1.125 0 01-1.667-.986V5.653z" />
                </svg>
              </div>
              Automated Recording
            </dt>
            <dd className="mt-2 text-base leading-7 text-gray-600">
              Schedule recordings or start immediate captures from internet radio streams.
              Support for HLS, HTTP/HTTPS, RTMP, and MMS protocols.
            </dd>
          </div>

          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-gray-900">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3-14.5v13.5A2.25 2.25 0 0 1 14.5 19h-8.25A2.25 2.25 0 0 1 4 16.75V5.25A2.25 2.25 0 0 1 6.25 3h8.25A2.25 2.25 0 0 1 16.5 5.25v3.5" />
                </svg>
              </div>
              File Management
            </dt>
            <dd className="mt-2 text-base leading-7 text-gray-600">
              Organize, search, and manage your recordings. Convert between formats
              and download files with metadata preservation.
            </dd>
          </div>

          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-gray-900">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189l2.9-2.9a3 3 0 003.11.11l1.5.75a1.5 1.5 0 01.44 2.48L18.76 15.44a6.01 6.01 0 00-.189 1.5m-9.9-2.25H6.75a1.5 1.5 0 01-1.5-1.5V8.25a1.5 1.5 0 011.5-1.5h3.75m3.75 0V6a1.5 1.5 0 011.5-1.5h3.75A1.5 1.5 0 0119.5 6v3m-11.5.5v4.5a1.5 1.5 0 001.5 1.5h3.75a1.5 1.5 0 001.5-1.5v-3.5" />
                </svg>
              </div>
              AI Analysis
            </dt>
            <dd className="mt-2 text-base leading-7 text-gray-600">
              Generate transcripts, summaries, and extract keywords from recordings
              using AI services. Speaker identification and content analysis.
            </dd>
          </div>

          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-gray-900">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75A1.125 1.125 0 012.25 18.375m.75 1.125v-11.25A1.125 1.125 0 013.375 6.25h14.25A1.125 1.125 0 0118.75 7.375v11.25A1.125 1.125 0 0117.625 19.5m-14.25 0V6.75A1.125 1.125 0 014.5 5.625h13.5A1.125 1.125 0 0119.5 6.75v12.75" />
                </svg>
              </div>
              Web Dashboard
            </dt>
            <dd className="mt-2 text-base leading-7 text-gray-600">
              Monitor system status, manage recordings, and control schedules
              through an intuitive web interface with real-time updates.
            </dd>
          </div>
        </dl>
      </div>
    </div>
  )
}

export default HomePage
