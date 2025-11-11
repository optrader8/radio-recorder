import { createFileRoute } from '@tanstack/react-router'
import RadioPlayer from '@/components/RadioPlayer'
import RecordingRecorder from '@/components/RecordingRecorder'
import { useAuthStore } from '@/stores/auth'

export const Route = createFileRoute('/radio-player')({
  component: RadioPlayerPage,
})

function RadioPlayerPage() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)

  if (!token) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="rounded-md bg-yellow-100 p-4 text-yellow-800">
          로그인이 필요합니다.
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 text-3xl font-bold text-gray-900">라디오 플레이어</h1>

      <div className="grid gap-8 md:grid-cols-2">
        {/* Radio Player */}
        <div>
          <RadioPlayer userId={user?.id || 'default'} />
        </div>

        {/* Recording Recorder */}
        <div>
          <RecordingRecorder userId={user?.id || 'default'} />
        </div>
      </div>

      {/* Information Section */}
      <div className="mt-12 rounded-lg border border-gray-300 bg-white p-6">
        <h2 className="mb-4 text-xl font-bold text-gray-900">기능 안내</h2>
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <h3 className="mb-2 font-semibold text-gray-900">라디오 재생기</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✓ 실시간 라디오 스트리밍 재생</li>
              <li>✓ 음량 조절 및 일시정지 제어</li>
              <li>✓ 비트레이트 선택 (64~320 kbps)</li>
              <li>✓ 광고 감지 및 회피 (skip_ads)</li>
            </ul>
          </div>

          <div>
            <h3 className="mb-2 font-semibold text-gray-900">녹음 제어기</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✓ 라이브 녹음 시작/중지</li>
              <li>✓ 녹음 일시정지/재개</li>
              <li>✓ 실시간 파일 크기 및 진행도 표시</li>
              <li>✓ 다양한 포맷 및 비트레이트 지원</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 rounded-md bg-blue-50 p-4 text-sm text-blue-800">
          <p className="font-semibold">WebSocket 실시간 업데이트</p>
          <p className="mt-1">
            플레이어와 녹음기는 WebSocket을 통해 실시간으로 상태 업데이트를 받습니다. 연결이 끊어지면 자동으로 재연결됩니다.
          </p>
        </div>
      </div>
    </div>
  )
}
