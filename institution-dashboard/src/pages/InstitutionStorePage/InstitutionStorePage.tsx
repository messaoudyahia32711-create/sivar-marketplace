import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  MessageCircle, ChevronRight, ChevronLeft, ShoppingCart, Star,
  MapPin, CheckCircle, Package, Briefcase, Building2, X, Clock, Tag
} from 'lucide-react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ════════════════════════════════════════════════════
// Types
// ════════════════════════════════════════════════════
interface StoreData {
  id: number
  name: string
  description: string
  logo: string | null
  banner: string | null
  phone: string
  wilaya: { id: number; name: string } | null
  location_detail: string
  manager_name: string
  return_policy: string
  is_verified: boolean
}

interface VendorInfo {
  username: string
  full_name: string
  role: string
  is_verified: boolean
  phone: string
}

interface ProductImage {
  id: number
  image: string
  alt_text: string
  order: number
}

interface Product {
  id: number
  name: string
  price: string
  discount_price: string | null
  image_main: string | null
  images: ProductImage[]
  category_name: string
  avg_rating: number | null
  reviews_count: number
  is_featured: boolean
  stock_status: 'ok' | 'low' | 'critical' | 'out'
  description?: string
}

interface ServiceImage {
  id: number
  image: string
  alt_text: string
  order: number
}

interface Service {
  id: number
  name: string
  price: string
  description: string
  category_name: string
  image_main: string | null
  images: ServiceImage[]
  avg_rating: number | null
  duration_hours: number | null
}

interface PublicStoreResponse {
  store: StoreData
  vendor: VendorInfo
  products: Product[]
  services: Service[]
}

type ModalItem = {
  type: 'product'
  data: Product
} | {
  type: 'service'
  data: Service
}

// ════════════════════════════════════════════════════
// Helpers
// ════════════════════════════════════════════════════
const fmt = (val: string | number) =>
  new Intl.NumberFormat('ar-DZ').format(Number(val)) + ' دج'

const IMG_PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMkEyQTJBIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZpbGw9IiM2NjYiIGZvbnQtc2l6ZT0iMjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiPuKShOKShOKShDwvdGV4dD48L3N2Zz4='

function getAllImages(item: ModalItem): string[] {
  const imgs: string[] = []
  if (item.type === 'product') {
    if (item.data.image_main) imgs.push(item.data.image_main)
    item.data.images?.forEach(img => { if (img.image && !imgs.includes(img.image)) imgs.push(img.image) })
  } else {
    if (item.data.image_main) imgs.push(item.data.image_main)
    item.data.images?.forEach(img => { if (img.image && !imgs.includes(img.image)) imgs.push(img.image) })
  }
  if (imgs.length === 0) imgs.push(IMG_PLACEHOLDER)
  return imgs
}

// ════════════════════════════════════════════════════
// Detail Modal
// ════════════════════════════════════════════════════
function DetailModal({ item, onClose }: { item: ModalItem; onClose: () => void }) {
  const [currentImg, setCurrentImg] = useState(0)
  const images = getAllImages(item)
  const isProduct = item.type === 'product'
  const d = item.data

  const nextImg = useCallback(() => setCurrentImg(i => (i + 1) % images.length), [images.length])
  const prevImg = useCallback(() => setCurrentImg(i => (i - 1 + images.length) % images.length), [images.length])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft') nextImg()
      if (e.key === 'ArrowRight') prevImg()
    }
    document.addEventListener('keydown', handler)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handler)
      document.body.style.overflow = ''
    }
  }, [onClose, nextImg, prevImg])

  const badgeLabel = isProduct
    ? ((d as Product).discount_price ? 'خصم' : (d as Product).is_featured ? 'مميز' : null)
    : null

  const isOut = isProduct && (d as Product).stock_status === 'out'

  return (
    <>
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, zIndex: 2000, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)', animation: 'fadeIn 0.3s ease' }} />
      <div style={{ position: 'fixed', inset: 0, zIndex: 2001, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px', pointerEvents: 'none' }}>
        <div style={{ pointerEvents: 'auto', background: '#111', borderRadius: 24, maxWidth: 560, width: '100%', maxHeight: '90vh', overflowY: 'auto', border: '1px solid rgba(212,175,55,0.15)', boxShadow: '0 25px 80px rgba(0,0,0,0.7)', animation: 'modalSlideUp 0.4s ease', direction: 'rtl', fontFamily: 'Tajawal, sans-serif' }}>
          {/* Image Gallery */}
          <div style={{ position: 'relative', width: '100%', aspectRatio: '4/3', background: '#0a0a0a', borderRadius: '24px 24px 0 0', overflow: 'hidden' }}>
            <img src={images[currentImg]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'opacity 0.3s' }} onError={(e) => { (e.target as HTMLImageElement).src = IMG_PLACEHOLDER }} />
            <button onClick={onClose} style={{ position: 'absolute', top: 14, left: 14, width: 36, height: 36, borderRadius: 12, background: 'rgba(0,0,0,0.6)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', backdropFilter: 'blur(8px)', transition: 'background 0.2s' }} onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,175,55,0.8)'; e.currentTarget.style.color = '#0F0F0F' }} onMouseLeave={e => { e.currentTarget.style.background = 'rgba(0,0,0,0.6)'; e.currentTarget.style.color = '#fff' }}>
              <X style={{ width: 18, height: 18 }} />
            </button>
            {badgeLabel && (
              <div style={{ position: 'absolute', top: 14, right: 14, background: 'rgba(0,0,0,0.7)', color: '#D4AF37', padding: '5px 16px', borderRadius: 20, fontSize: '0.85rem', border: '1px solid #D4AF37', backdropFilter: 'blur(5px)', fontWeight: 700 }}>{badgeLabel}</div>
            )}
            {images.length > 1 && (
              <>
                <button onClick={prevImg} style={{ position: 'absolute', top: '50%', right: 10, transform: 'translateY(-50%)', width: 38, height: 38, borderRadius: '50%', background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', backdropFilter: 'blur(4px)', transition: 'background 0.2s' }} onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,175,55,0.7)' }} onMouseLeave={e => { e.currentTarget.style.background = 'rgba(0,0,0,0.5)' }}>
                  <ChevronRight style={{ width: 20, height: 20 }} />
                </button>
                <button onClick={nextImg} style={{ position: 'absolute', top: '50%', left: 10, transform: 'translateY(-50%)', width: 38, height: 38, borderRadius: '50%', background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', backdropFilter: 'blur(4px)', transition: 'background 0.2s' }} onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,175,55,0.7)' }} onMouseLeave={e => { e.currentTarget.style.background = 'rgba(0,0,0,0.5)' }}>
                  <ChevronLeft style={{ width: 20, height: 20 }} />
                </button>
              </>
            )}
            {images.length > 1 && (
              <div style={{ position: 'absolute', bottom: 12, left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: 6 }}>
                {images.map((_, idx) => (
                  <button key={idx} onClick={() => setCurrentImg(idx)} style={{ width: idx === currentImg ? 24 : 8, height: 8, borderRadius: 4, border: 'none', cursor: 'pointer', background: idx === currentImg ? '#D4AF37' : 'rgba(255,255,255,0.4)', transition: 'all 0.3s' }} />
                ))}
              </div>
            )}
            {images.length > 1 && (
              <div style={{ position: 'absolute', bottom: 12, right: 12, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', padding: '3px 10px', borderRadius: 12, color: '#ccc', fontSize: '0.75rem' }}>{currentImg + 1} / {images.length}</div>
            )}
            <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '40%', background: 'linear-gradient(to top, #111, transparent)', pointerEvents: 'none' }} />
          </div>

          {/* Thumbnails */}
          {images.length > 1 && (
            <div style={{ display: 'flex', gap: 8, padding: '12px 20px', overflowX: 'auto', background: '#111' }}>
              {images.map((img, idx) => (
                <button key={idx} onClick={() => setCurrentImg(idx)} style={{ width: 56, height: 56, borderRadius: 10, overflow: 'hidden', flexShrink: 0, border: idx === currentImg ? '2px solid #D4AF37' : '2px solid rgba(255,255,255,0.1)', opacity: idx === currentImg ? 1 : 0.5, transition: 'all 0.3s', cursor: 'pointer', boxShadow: idx === currentImg ? '0 0 12px rgba(212,175,55,0.3)' : 'none' }}>
                  <img src={img} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={(e) => { (e.target as HTMLImageElement).src = IMG_PLACEHOLDER }} />
                </button>
              ))}
            </div>
          )}

          {/* Details */}
          <div style={{ padding: '20px 24px 28px' }}>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#fff', marginBottom: 8, lineHeight: 1.4 }}>{d.name}</h2>
            {d.avg_rating && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                {[1,2,3,4,5].map(s => (<Star key={s} style={{ width: 14, height: 14, fill: s <= Math.round(d.avg_rating!) ? '#D4AF37' : 'none', color: '#D4AF37' }} />))}
                <span style={{ color: '#888', fontSize: '0.85rem', marginRight: 4 }}>({d.avg_rating?.toFixed(1)})</span>
                {isProduct && (d as Product).reviews_count > 0 && <span style={{ color: '#666', fontSize: '0.8rem' }}>· {(d as Product).reviews_count} تقييم</span>}
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
              <span style={{ fontSize: '1.6rem', color: '#D2691E', fontWeight: 900 }}>{fmt(d.price)}</span>
              {isProduct && (d as Product).discount_price && (
                <>
                  <span style={{ fontSize: '1rem', color: '#666', textDecoration: 'line-through' }}>{fmt((d as Product).discount_price!)}</span>
                  <span style={{ background: 'rgba(212,175,55,0.15)', color: '#D4AF37', padding: '2px 10px', borderRadius: 20, fontSize: '0.8rem', fontWeight: 700 }}>خصم</span>
                </>
              )}
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 14, padding: '14px 16px', marginBottom: 20, border: '1px solid rgba(255,255,255,0.05)' }}>
              <h4 style={{ color: '#D4AF37', fontSize: '0.9rem', fontWeight: 700, marginBottom: 8 }}>الوصف</h4>
              <p style={{ color: '#aaa', fontSize: '0.9rem', lineHeight: 1.9 }}>{d.description || 'لا يوجد وصف متوفر.'}</p>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 24 }}>
              {isProduct && (
                <>
                  <div style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.15)', borderRadius: 12, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Tag style={{ width: 14, height: 14, color: '#D4AF37' }} />
                    <div><div style={{ fontSize: '0.7rem', color: '#888' }}>الفئة</div><div style={{ fontSize: '0.85rem', color: '#D4AF37', fontWeight: 700 }}>{(d as Product).category_name || 'عام'}</div></div>
                  </div>
                  <div style={{ background: (d as Product).stock_status === 'out' ? 'rgba(239,68,68,0.08)' : 'rgba(16,185,129,0.08)', border: `1px solid ${(d as Product).stock_status === 'out' ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)'}`, borderRadius: 12, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Package style={{ width: 14, height: 14, color: (d as Product).stock_status === 'out' ? '#ef4444' : '#10b981' }} />
                    <div><div style={{ fontSize: '0.7rem', color: '#888' }}>المخزون</div><div style={{ fontSize: '0.85rem', fontWeight: 700, color: (d as Product).stock_status === 'out' ? '#ef4444' : '#10b981' }}>{(d as Product).stock_status === 'out' ? 'نفذ' : (d as Product).stock_status === 'critical' ? 'ينفذ قريباً' : 'متوفر'}</div></div>
                  </div>
                </>
              )}
              {!isProduct && (d as Service).duration_hours && (
                <div style={{ background: 'rgba(210,105,30,0.08)', border: '1px solid rgba(210,105,30,0.15)', borderRadius: 12, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Clock style={{ width: 14, height: 14, color: '#D2691E' }} />
                  <div><div style={{ fontSize: '0.7rem', color: '#888' }}>المدة</div><div style={{ fontSize: '0.85rem', color: '#D2691E', fontWeight: 700 }}>{(d as Service).duration_hours} ساعة</div></div>
                </div>
              )}
              {!isProduct && (d as Service).category_name && (
                <div style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.15)', borderRadius: 12, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Tag style={{ width: 14, height: 14, color: '#D4AF37' }} />
                  <div><div style={{ fontSize: '0.7rem', color: '#888' }}>الفئة</div><div style={{ fontSize: '0.85rem', color: '#D4AF37', fontWeight: 700 }}>{(d as Service).category_name}</div></div>
                </div>
              )}
            </div>
            <button disabled={isOut} style={{ width: '100%', padding: '14px', background: isOut ? '#333' : 'linear-gradient(135deg, #D4AF37, #c9a22e)', color: isOut ? '#666' : '#0F0F0F', border: 'none', borderRadius: 14, fontFamily: 'Tajawal, sans-serif', fontWeight: 900, fontSize: '1.05rem', cursor: isOut ? 'not-allowed' : 'pointer', transition: 'transform 0.2s, box-shadow 0.2s', boxShadow: isOut ? 'none' : '0 8px 24px rgba(212,175,55,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }} onMouseEnter={e => { if (!isOut) e.currentTarget.style.transform = 'translateY(-2px)' }} onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)' }}>
              {isProduct ? (<><ShoppingCart style={{ width: 18, height: 18 }} />{isOut ? 'غير متوفر حالياً' : 'أضف للسلة'}</>) : (<><Briefcase style={{ width: 18, height: 18 }} />اطلب الخدمة</>)}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

// ════════════════════════════════════════════════════
// Product Card
// ════════════════════════════════════════════════════
function ProductCard({ product, onClick }: { product: Product; onClick: () => void }) {
  const [hovered, setHovered] = useState(false)
  const badgeLabel = product.discount_price ? 'خصم' : product.is_featured ? 'مميز' : null
  const isOut = product.stock_status === 'out'

  return (
    <div onClick={onClick} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
      style={{ background: 'var(--black-card)', borderRadius: '20px', overflow: 'hidden', position: 'relative', transition: 'transform 0.4s ease, box-shadow 0.4s ease', transform: hovered ? 'translateY(-10px) rotateX(3deg)' : 'translateY(0)', boxShadow: hovered ? '0 20px 40px rgba(212, 175, 55, 0.2)' : '8px 8px 20px rgba(0,0,0,0.6)', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer' }}
    >
      <div style={{ width: '100%', height: '200px', position: 'relative', overflow: 'hidden', background: '#222' }}>
        <img src={product.image_main || IMG_PLACEHOLDER} alt={product.name} style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.5s', transform: hovered ? 'scale(1.1)' : 'scale(1)' }} onError={(e) => { (e.target as HTMLImageElement).src = IMG_PLACEHOLDER }} />
        {badgeLabel && <div style={{ position: 'absolute', top: 15, right: 15, background: 'rgba(0,0,0,0.7)', color: 'var(--gold)', padding: '5px 15px', borderRadius: '20px', fontSize: '0.8rem', border: '1px solid var(--gold)', backdropFilter: 'blur(5px)' }}>{badgeLabel}</div>}
        {product.images && product.images.length > 0 && <div style={{ position: 'absolute', bottom: 10, left: 10, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', padding: '3px 8px', borderRadius: 8, color: '#ccc', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: 4 }}>📷 {product.images.length + (product.image_main ? 1 : 0)}</div>}
        {isOut && <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><span style={{ color: '#ef4444', fontWeight: 900, fontSize: '1.1rem' }}>نفذ المخزون</span></div>}
      </div>
      <div style={{ padding: '20px' }}>
        {product.avg_rating && <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 8 }}>{[1,2,3,4,5].map(s => <Star key={s} style={{ width: 12, height: 12, fill: s <= Math.round(product.avg_rating!) ? 'var(--gold)' : 'none', color: 'var(--gold)' }} />)}<span style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginRight: 4 }}>({product.avg_rating?.toFixed(1)})</span></div>}
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-white)' }}>{product.name}</h3>
        <div style={{ marginBottom: 15 }}>
          <span style={{ fontSize: '1.3rem', color: 'var(--sand-orange)', fontWeight: 900 }}>{fmt(product.price)}</span>
          {product.discount_price && <span style={{ fontSize: '0.85rem', color: 'var(--text-gray)', textDecoration: 'line-through', marginRight: 8 }}>{fmt(product.discount_price)}</span>}
        </div>
        <button disabled={isOut} onClick={(e) => e.stopPropagation()} style={{ width: '100%', padding: '12px', background: 'transparent', color: 'var(--gold)', border: '2px solid var(--gold)', borderRadius: '10px', fontFamily: 'Tajawal, sans-serif', fontWeight: 'bold', cursor: isOut ? 'not-allowed' : 'pointer', transition: 'all 0.3s', opacity: isOut ? 0.5 : 1 }} onMouseEnter={(e) => { if (!isOut) { e.currentTarget.style.background = 'var(--gold)'; e.currentTarget.style.color = '#0F0F0F' } }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--gold)' }}>
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}><ShoppingCart style={{ width: 16, height: 16 }} />{isOut ? 'غير متوفر' : 'أضف للسلة'}</span>
        </button>
      </div>
    </div>
  )
}

// ════════════════════════════════════════════════════
// Service Card
// ════════════════════════════════════════════════════
function ServiceCard({ service, onClick }: { service: Service; onClick: () => void }) {
  const [hovered, setHovered] = useState(false)
  const img = service.image_main || service.images?.[0]?.image || IMG_PLACEHOLDER

  return (
    <div onClick={onClick} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
      style={{ background: 'var(--black-card)', borderRadius: '20px', overflow: 'hidden', position: 'relative', transition: 'transform 0.4s ease, box-shadow 0.4s ease', transform: hovered ? 'translateY(-10px)' : 'translateY(0)', boxShadow: hovered ? '0 20px 40px rgba(210, 105, 30, 0.2)' : '8px 8px 20px rgba(0,0,0,0.6)', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer' }}
    >
      <div style={{ width: '100%', height: '200px', overflow: 'hidden', background: '#222', position: 'relative' }}>
        <img src={img} alt={service.name} style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.5s', transform: hovered ? 'scale(1.1)' : 'scale(1)' }} onError={(e) => { (e.target as HTMLImageElement).src = IMG_PLACEHOLDER }} />
        {service.images && service.images.length > 0 && <div style={{ position: 'absolute', bottom: 10, left: 10, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', padding: '3px 8px', borderRadius: 8, color: '#ccc', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: 4 }}>📷 {service.images.length + (service.image_main ? 1 : 0)}</div>}
      </div>
      <div style={{ padding: '20px' }}>
        {service.category_name && <span style={{ display: 'inline-block', fontSize: '0.75rem', color: 'var(--sand-light)', border: '1px solid rgba(210,105,30,0.4)', borderRadius: '20px', padding: '2px 10px', marginBottom: 8 }}>{service.category_name}</span>}
        {service.avg_rating && <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6 }}>{[1,2,3,4,5].map(s => <Star key={s} style={{ width: 12, height: 12, fill: s <= Math.round(service.avg_rating!) ? 'var(--gold)' : 'none', color: 'var(--gold)' }} />)}</div>}
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-white)' }}>{service.name}</h3>
        <div style={{ fontSize: '1.3rem', color: 'var(--sand-orange)', fontWeight: 900, marginBottom: 15 }}>{fmt(service.price)}</div>
        <button onClick={(e) => e.stopPropagation()} style={{ width: '100%', padding: '12px', background: 'transparent', color: 'var(--gold)', border: '2px solid var(--gold)', borderRadius: '10px', fontFamily: 'Tajawal, sans-serif', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--gold)'; e.currentTarget.style.color = '#0F0F0F' }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--gold)' }}>
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}><Briefcase style={{ width: 16, height: 16 }} />اطلب الخدمة</span>
        </button>
      </div>
    </div>
  )
}

function CardSkeleton() {
  return (
    <div style={{ background: 'var(--black-card)', borderRadius: '20px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)' }}>
      <div style={{ height: 200, background: 'linear-gradient(90deg, #1e1e1e 25%, #2a2a2a 50%, #1e1e1e 75%)', backgroundSize: '200% 100%' }} />
      <div style={{ padding: 20 }}>
        <div style={{ height: 16, background: '#2a2a2a', borderRadius: 8, marginBottom: 12, width: '70%' }} />
        <div style={{ height: 24, background: '#2a2a2a', borderRadius: 8, marginBottom: 16, width: '40%' }} />
        <div style={{ height: 40, background: '#2a2a2a', borderRadius: 10 }} />
      </div>
    </div>
  )
}

// ════════════════════════════════════════════════════
// Main InstitutionStorePage Component
// ════════════════════════════════════════════════════
export default function InstitutionStorePage() {
  const { username } = useParams<{ username: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'products' | 'services'>('products')
  const [showContactPulse, setShowContactPulse] = useState(true)
  const [modalItem, setModalItem] = useState<ModalItem | null>(null)

  useEffect(() => {
    const interval = setInterval(() => setShowContactPulse(p => !p), 3000)
    return () => clearInterval(interval)
  }, [])

  const { data, isLoading, error } = useQuery<PublicStoreResponse>({
    queryKey: ['public-store', username],
    queryFn: async () => {
      const res = await axios.get(`${API_BASE}/api/vendors/api/public/store/${username}/`)
      return res.data
    },
    enabled: !!username,
    retry: 1,
  })

  const storeStyles = `
    :root { --black-bg: #0F0F0F; --black-card: #1A1A1A; --gold: #D4AF37; --gold-shimmer: #F7E7CE; --sand-orange: #D2691E; --sand-light: #E07C24; --text-white: #FFFFFF; --text-gray: #B0B0B0; }
    .store-page-body { font-family: 'Tajawal', sans-serif; background-color: var(--black-bg); color: var(--text-white); background-image: radial-gradient(circle at 10% 20%, rgba(212, 175, 55, 0.05) 0%, transparent 20%), radial-gradient(circle at 90% 80%, rgba(210, 105, 30, 0.05) 0%, transparent 20%); min-height: 100vh; direction: rtl; }
    @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
    .skeleton-animate { animation: shimmer 1.5s infinite linear; background: linear-gradient(90deg, #1e1e1e 25%, #2a2a2a 50%, #1e1e1e 75%); background-size: 200% 100%; }
    @keyframes float-btn { 0%, 100% { transform: translateX(-50%) translateY(0); } 50% { transform: translateX(-50%) translateY(-5px); } }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes modalSlideUp { from { opacity: 0; transform: translateY(40px) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
    .animate-fade-in-up { animation: fadeInUp 0.6s ease-out both; }
    .tab-active { background: linear-gradient(145deg, #D2691E, #E07C24) !important; color: white !important; transform: translateY(-5px) !important; box-shadow: 0 15px 30px rgba(210, 105, 30, 0.3) !important; border-bottom: 4px solid rgba(0,0,0,0.2) !important; }
    .tab-inactive:hover { background: #252525 !important; color: var(--gold) !important; transform: translateY(-2px) !important; }
    .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; padding: 0 20px; animation: fadeInUp 0.5s ease-out; }
    @media (max-width: 600px) { .products-grid { grid-template-columns: 1fr; padding: 0 10px; } }
  `

  if (error) {
    return (
      <div style={{ minHeight: '100vh', background: '#0F0F0F', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16, direction: 'rtl', fontFamily: 'Tajawal, sans-serif' }}>
        <Building2 style={{ width: 64, height: 64, color: '#D4AF37', opacity: 0.4 }} />
        <h2 style={{ color: '#fff', fontSize: '1.5rem' }}>المؤسسة غير موجودة</h2>
        <p style={{ color: '#888' }}>لم يتم العثور على هذه المؤسسة</p>
        <button onClick={() => navigate(-1)} style={{ padding: '10px 24px', background: '#D4AF37', color: '#0F0F0F', border: 'none', borderRadius: '50px', fontFamily: 'Tajawal, sans-serif', fontWeight: 700, cursor: 'pointer', fontSize: '1rem' }}>عودة</button>
      </div>
    )
  }

  const store = data?.store
  const vendor = data?.vendor
  const products = data?.products || []
  const services = data?.services || []

  return (
    <>
      <style>{storeStyles}</style>
      <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet" />

      {modalItem && <DetailModal item={modalItem} onClose={() => setModalItem(null)} />}

      <div className="store-page-body" style={{ position: 'relative' }}>
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 0, backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23D4AF37' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C%2Fg%3E%3C%2Fsvg%3E")` }} />

        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, height: 54, background: 'rgba(15, 15, 15, 0.9)', backdropFilter: 'blur(12px)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 20px', zIndex: 1000, borderBottom: '1px solid rgba(212, 175, 55, 0.1)' }}>
          <button onClick={() => navigate(-1)} style={{ width: 40, height: 40, borderRadius: 12, border: '1px solid rgba(212, 175, 55, 0.25)', background: 'rgba(26, 26, 26, 0.8)', color: '#D4AF37', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', transition: 'all 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.background = '#D4AF37'; e.currentTarget.style.color = '#0F0F0F' }} onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(26, 26, 26, 0.8)'; e.currentTarget.style.color = '#D4AF37' }} aria-label="عودة">
            <ChevronRight style={{ width: 20, height: 20 }} />
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Building2 style={{ width: 16, height: 16, color: '#D4AF37' }} />
            <span style={{ color: '#D4AF37', fontWeight: 700, fontSize: '0.9rem', fontFamily: 'Tajawal, sans-serif' }}>{store?.name || vendor?.username || 'المؤسسة'}</span>
          </div>
          <div style={{ width: 40 }} />
        </div>

        <button
          style={{ position: 'fixed', bottom: 30, left: '50%', transform: 'translateX(-50%)', display: 'flex', alignItems: 'center', gap: 10, padding: '14px 32px', background: 'linear-gradient(135deg, #D4AF37, #c9a22e)', color: '#0F0F0F', border: 'none', borderRadius: '50px', fontFamily: 'Tajawal, sans-serif', fontSize: '1.05rem', fontWeight: 900, cursor: 'pointer', zIndex: 1000, boxShadow: showContactPulse ? '0 8px 30px rgba(212, 175, 55, 0.5), 0 0 0 8px rgba(212, 175, 55, 0.1)' : '0 8px 30px rgba(212, 175, 55, 0.35)', transition: 'box-shadow 0.4s', animation: 'float-btn 3s ease-in-out infinite' }}
          onClick={() => { const phone = vendor?.phone || store?.phone; if (phone) window.open(`tel:${phone}`) }}
          id="contact-institution-btn"
        >
          <MessageCircle style={{ width: 22, height: 22, flexShrink: 0 }} />
          تواصل مع المؤسسة
        </button>

        <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 120, paddingTop: 54, position: 'relative', zIndex: 1 }}>
          <div style={{ position: 'relative', height: 380, borderRadius: '0 0 30px 30px', overflow: 'hidden', boxShadow: '0 15px 30px rgba(0,0,0,0.5)', marginBottom: 40 }}>
            {isLoading ? <div className="skeleton-animate" style={{ width: '100%', height: '100%' }} /> : (
              <div style={{ width: '100%', height: '100%', backgroundImage: store?.banner ? `url(${store.banner})` : `url(https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)`, backgroundSize: 'cover', backgroundPosition: 'center', filter: 'brightness(0.65)' }} />
            )}
            <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '60%', background: 'linear-gradient(to top, rgba(15,15,15,0.9), transparent)' }} />
            <div style={{ position: 'absolute', bottom: 25, right: 30, zIndex: 10 }}>
              <div style={{ background: 'linear-gradient(135deg, #0F0F0F, #1A1A1A)', padding: '15px 25px', borderRadius: 15, border: '1px solid rgba(212, 175, 55, 0.3)', boxShadow: '0 10px 20px rgba(0,0,0,0.3)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <h1 style={{ fontSize: '1.8rem', fontWeight: 900, background: 'linear-gradient(to right, #D4AF37, #F7E7CE)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: 1, fontFamily: 'Tajawal, sans-serif' }}>{isLoading ? '...' : (store?.name || `مؤسسة ${vendor?.username}`)}</h1>
                  {(vendor?.is_verified || store?.is_verified) && <CheckCircle style={{ width: 20, height: 20, color: '#D4AF37', flexShrink: 0 }} />}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ color: '#D2691E', fontSize: '0.9rem', fontWeight: 700 }}>مؤسسة معتمدة في Sivar</span>
                  {store?.wilaya && <span style={{ color: '#888', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 4 }}><MapPin style={{ width: 12, height: 12 }} />{store.wilaya.name}</span>}
                </div>
              </div>
            </div>
            <div style={{ position: 'absolute', top: 18, left: 20, display: 'flex', gap: 12 }}>
              <div style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)', padding: '6px 14px', borderRadius: 20, border: '1px solid rgba(212,175,55,0.2)', color: '#fff', fontSize: '0.8rem', fontFamily: 'Tajawal, sans-serif', display: 'flex', alignItems: 'center', gap: 6 }}><Package style={{ width: 14, height: 14, color: '#D4AF37' }} /><span>{isLoading ? '...' : products.length} منتج</span></div>
              <div style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)', padding: '6px 14px', borderRadius: 20, border: '1px solid rgba(210,105,30,0.2)', color: '#fff', fontSize: '0.8rem', fontFamily: 'Tajawal, sans-serif', display: 'flex', alignItems: 'center', gap: 6 }}><Briefcase style={{ width: 14, height: 14, color: '#D2691E' }} /><span>{isLoading ? '...' : services.length} خدمة</span></div>
            </div>
          </div>

          {store?.description && !isLoading && (
            <div className="animate-fade-in-up" style={{ margin: '0 20px 30px', padding: '16px 20px', background: 'rgba(212, 175, 55, 0.05)', borderRadius: 16, border: '1px solid rgba(212, 175, 55, 0.1)' }}>
              <p style={{ color: '#B0B0B0', fontSize: '0.95rem', lineHeight: 1.8 }}>{store.description}</p>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'center', gap: 20, marginBottom: 40, perspective: 1000 }}>
            {(['products', 'services'] as const).map((tab) => (
              <button key={tab} className={activeTab === tab ? 'tab-active' : 'tab-inactive'} onClick={() => setActiveTab(tab)}
                style={{ padding: '15px 40px', fontSize: '1.2rem', fontWeight: 700, fontFamily: 'Tajawal, sans-serif', border: 'none', borderRadius: '50px', cursor: 'pointer', transition: 'all 0.3s ease', background: activeTab === tab ? 'linear-gradient(145deg, #D2691E, #E07C24)' : '#1A1A1A', color: activeTab === tab ? '#fff' : '#B0B0B0', borderBottom: `4px solid ${activeTab === tab ? 'rgba(0,0,0,0.2)' : 'transparent'}`, transform: activeTab === tab ? 'translateY(-5px)' : 'translateY(0)', boxShadow: activeTab === tab ? '0 15px 30px rgba(210, 105, 30, 0.3)' : '0 5px 15px rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', gap: 8 }}
              >
                {tab === 'products' ? (<><Package style={{ width: 18, height: 18 }} /> المنتجات{' '}{!isLoading && <span style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 20, padding: '1px 8px', fontSize: '0.85rem' }}>{products.length}</span>}</>) : (<><Briefcase style={{ width: 18, height: 18 }} /> الخدمات{' '}{!isLoading && <span style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 20, padding: '1px 8px', fontSize: '0.85rem' }}>{services.length}</span>}</>)}
              </button>
            ))}
          </div>

          {activeTab === 'products' && (
            <div className="products-grid">
              {isLoading ? Array(4).fill(0).map((_, i) => <CardSkeleton key={i} />) : products.length === 0
                ? <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '60px 20px' }}><Package style={{ width: 64, height: 64, color: '#D4AF37', opacity: 0.2, margin: '0 auto 16px' }} /><p style={{ color: '#888', fontSize: '1.1rem' }}>لا توجد منتجات متاحة حالياً</p></div>
                : products.map((p, i) => (<div key={p.id} className="animate-fade-in-up" style={{ animationDelay: `${i * 0.08}s` }}><ProductCard product={p} onClick={() => setModalItem({ type: 'product', data: p })} /></div>))}
            </div>
          )}

          {activeTab === 'services' && (
            <div className="products-grid">
              {isLoading ? Array(4).fill(0).map((_, i) => <CardSkeleton key={i} />) : services.length === 0
                ? <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '60px 20px' }}><Briefcase style={{ width: 64, height: 64, color: '#D2691E', opacity: 0.2, margin: '0 auto 16px' }} /><p style={{ color: '#888', fontSize: '1.1rem' }}>لا توجد خدمات متاحة حالياً</p></div>
                : services.map((s, i) => (<div key={s.id} className="animate-fade-in-up" style={{ animationDelay: `${i * 0.08}s` }}><ServiceCard service={s} onClick={() => setModalItem({ type: 'service', data: s })} /></div>))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
