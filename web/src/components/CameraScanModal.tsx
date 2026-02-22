import { useEffect, useRef, useState, useCallback } from 'react'
import { apiUrl } from '../lib/api'
import './CameraScanModal.css'

const AUTO_CAPTURE_INTERVAL_MS = 500

interface Box {
  x: number
  y: number
  w: number
  h: number
}

interface CameraScanModalProps {
  open: boolean
  onClose: () => void
  onCardsDetected: (cards: number[]) => void
  scanning: boolean
  setScanning: (v: boolean) => void
}

export default function CameraScanModal({
  open,
  onClose,
  onCardsDetected,
  scanning,
  setScanning,
}: CameraScanModalProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const overlayRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [boxes, setBoxes] = useState<Box[]>([])
  const [imgSize, setImgSize] = useState({ w: 1, h: 1 })

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setBoxes([])
  }, [])

  const onCardsDetectedRef = useRef(onCardsDetected)
  const scanningRef = useRef(false)
  onCardsDetectedRef.current = onCardsDetected
  scanningRef.current = scanning

  const captureAndScan = useCallback(async () => {
    const video = videoRef.current
    if (!video || !video.srcObject || scanningRef.current) return
    scanningRef.current = true
    setScanning(true)
    setError(null)
    try {
      const canvas = document.createElement('canvas')
      const maxDim = 640
      let w = video.videoWidth
      let h = video.videoHeight
      if (!w || !h) return
      if (w > maxDim || h > maxDim) {
        if (w > h) {
          h = Math.round((h * maxDim) / w)
          w = maxDim
        } else {
          w = Math.round((w * maxDim) / h)
          h = maxDim
        }
      }
      canvas.width = w
      canvas.height = h
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.save()
      ctx.translate(w, 0)
      ctx.scale(-1, 1)
      ctx.drawImage(video, 0, 0, w, h)
      ctx.restore()
      const blob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob(resolve, 'image/jpeg', 0.9)
      )
      if (!blob) return
      const fd = new FormData()
      fd.append('file', blob, 'capture.jpg')
      const res = await fetch(apiUrl('/api/scan-cards'), { method: 'POST', body: fd })
      const data = await res.json().catch(() => ({}))
      const cards = (data.cards ?? []) as number[]
      const rawBoxes = (data.boxes ?? []) as Box[]
      const iw = data.img_width || w
      const ih = data.img_height || h
      setImgSize({ w: iw, h: ih })
      setBoxes(rawBoxes)
      if (cards.length >= 1) {
        onCardsDetectedRef.current(cards)
      }
    } catch {
      setBoxes([])
    } finally {
      scanningRef.current = false
      setScanning(false)
    }
  }, [setScanning])

  useEffect(() => {
    if (!open) {
      stopStream()
      setError(null)
      return
    }
    setError(null)
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: 'environment' },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        })
        streamRef.current = stream
        if (videoRef.current) videoRef.current.srcObject = stream
        intervalRef.current = setInterval(captureAndScan, AUTO_CAPTURE_INTERVAL_MS)
      } catch {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
          })
          streamRef.current = stream
          if (videoRef.current) videoRef.current.srcObject = stream
          intervalRef.current = setInterval(captureAndScan, AUTO_CAPTURE_INTERVAL_MS)
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Camera access denied')
        }
      }
    }
    startCamera()
    return stopStream
  }, [open, stopStream, captureAndScan])

  useEffect(() => {
    const video = videoRef.current
    const overlay = overlayRef.current
    if (!video || !overlay || boxes.length === 0 || !imgSize.w) return
    const draw = () => {
      const rect = video.getBoundingClientRect()
      const vw = video.videoWidth
      const vh = video.videoHeight
      if (!vw || !vh) return
      overlay.width = rect.width
      overlay.height = rect.height
      const ctx = overlay.getContext('2d')
      if (!ctx) return
      ctx.clearRect(0, 0, overlay.width, overlay.height)
      const scaleX = overlay.width / imgSize.w
      const scaleY = overlay.height / imgSize.h
      ctx.strokeStyle = 'rgba(0, 255, 100, 0.9)'
      ctx.lineWidth = 3
      boxes.forEach((b) => {
        const ox = overlay.width - (b.x + b.w) * scaleX
        ctx.strokeRect(ox, b.y * scaleY, b.w * scaleX, b.h * scaleY)
      })
    }
    draw()
    const obs = new ResizeObserver(draw)
    obs.observe(video)
    return () => obs.disconnect()
  }, [boxes, imgSize])

  if (!open) return null

  return (
    <div className="camera-modal-overlay" onClick={onClose}>
      <div className="camera-modal" onClick={(e) => e.stopPropagation()}>
        <div className="camera-modal-header">
          <h3>Scan cards (live camera)</h3>
          <button type="button" className="camera-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        <div className="camera-video-wrap">
          <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
          <canvas ref={overlayRef} className="camera-overlay" aria-hidden />
          {error && <p className="camera-error">{error}</p>}
          {scanning && <span className="camera-scanning">Scanning…</span>}
        </div>
        <p className="camera-hint">Hold cards in frame — green boxes show detected regions. Use good lighting and a contrasting background for best results.</p>
      </div>
    </div>
  )
}
