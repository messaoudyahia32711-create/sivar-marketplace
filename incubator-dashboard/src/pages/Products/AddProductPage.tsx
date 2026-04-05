import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  ArrowRight, Upload, X, Image as ImageIcon, Plus,
  Package, DollarSign, Layers, FileText, Loader2, Check, Star
} from 'lucide-react'
import { toast } from 'sonner'
import { apiClient, generalClient } from '../../api/client'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Textarea } from '../../components/ui/textarea'
import { 
  Select, SelectContent, SelectItem, 
  SelectTrigger, SelectValue 
} from '../../components/ui/select'
import { cn } from '../../lib/utils'

const STEPS = [
  { id: 'info',    label: 'المعلومات الأساسية', icon: FileText },
  { id: 'pricing', label: 'التسعير والمخزون',   icon: DollarSign },
  { id: 'media',   label: 'الصور والوسائط',     icon: ImageIcon },
  { id: 'review',  label: 'المراجعة والنشر',    icon: Check },
]

export default function AddProductPage() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [mainImage, setMainImage] = useState<File | null>(null)
  const [galleryImages, setGalleryImages] = useState<File[]>([])
  const [dragActive, setDragActive] = useState(false)
  
  const [form, setForm] = useState({
    name: '', description: '', category: '', 
    price: '', discount_price: '', stock: '', 
    is_featured: false
  })

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => generalClient.get('/products/categories/').then(r => r.data)
  })

  const updateForm = (field: string, value: any) => setForm(prev => ({ ...prev, [field]: value }))

  // Drag & Drop
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
    else if (e.type === 'dragleave') setDragActive(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation()
    setDragActive(false)
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
    if (files.length > 0) {
      if (!mainImage) { setMainImage(files[0]); files.shift() }
      setGalleryImages(prev => [...prev, ...files].slice(0, 5))
    }
  }, [mainImage])

  const removeGalleryImage = (idx: number) => setGalleryImages(prev => prev.filter((_, i) => i !== idx))

  // Completion percentage
  const completion = Math.round(
    ([form.name, form.category, form.description, form.price, form.stock, mainImage].filter(Boolean).length / 6) * 100
  )

  const handleSubmit = async () => {
    if (!form.name || !form.category || !form.price || !form.stock) {
      toast.error('يرجى ملء جميع الحقول المطلوبة')
      return
    }
    setLoading(true)
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('description', form.description)
    formData.append('category', form.category)
    formData.append('price', form.price)
    if (form.discount_price) formData.append('discount_price', form.discount_price)
    formData.append('stock', form.stock)
    formData.append('is_featured', String(form.is_featured))
    if (mainImage) formData.set('image_main', mainImage)
    galleryImages.forEach(img => formData.append('uploaded_images', img))

    try {
      await apiClient.post('/products/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      toast.success('تمت إضافة المنتج بنجاح! 🎉')
      navigate('/products')
    } catch (err: any) {
      const errors = err.response?.data
      const msg = errors ? Object.values(errors).flat().join(' • ') : 'حدث خطأ أثناء الإضافة'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => navigate('/products')}>
            <ArrowRight className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-black">إضافة منتج جديد</h1>
            <p className="text-muted-foreground text-sm mt-1">أنشئ منتجاً جديداً وابدأ بيعه في متجرك</p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-3">
          <div className="text-left">
            <p className="text-xs text-muted-foreground">اكتمال النموذج</p>
            <p className="text-lg font-bold text-blue-400">{completion}%</p>
          </div>
          <div className="w-16 h-16 relative">
            <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="2" className="text-white/5" />
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray={`${completion}, 100`} className="text-blue-500" strokeLinecap="round" />
            </svg>
            <Package className="w-5 h-5 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-blue-400" />
          </div>
        </div>
      </div>

      {/* Step Indicators */}
      <div className="glass-card border-none p-4">
        <div className="flex items-center justify-between">
          {STEPS.map((step, idx) => (
            <button
              key={step.id}
              onClick={() => setCurrentStep(idx)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all text-sm font-medium flex-1 justify-center",
                idx === currentStep
                  ? "bg-blue-500/20 text-blue-400 shadow-lg shadow-blue-500/10"
                  : idx < currentStep
                    ? "text-emerald-400 bg-emerald-500/10"
                    : "text-muted-foreground hover:bg-white/5"
              )}
            >
              <step.icon className="w-4 h-4" />
              <span className="hidden sm:inline">{step.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="glass-card border-none p-8 animate-scale-in" key={currentStep}>
        {/* ── Step 1: Basic Info ── */}
        {currentStep === 0 && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold">المعلومات الأساسية</h2>
                <p className="text-sm text-muted-foreground">أدخل اسم المنتج وتفاصيله</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-semibold">اسم المنتج <span className="text-red-400">*</span></Label>
                <Input 
                  value={form.name} onChange={e => updateForm('name', e.target.value)}
                  placeholder="مثلاً: قفطان جزائري عصري" 
                  className="h-12 rounded-xl bg-white/5 border-white/10 text-right"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-semibold">التصنيف <span className="text-red-400">*</span></Label>
                <Select value={form.category} onValueChange={v => updateForm('category', v)}>
                  <SelectTrigger className="h-12 rounded-xl bg-white/5 border-white/10 text-right">
                    <SelectValue placeholder="اختر تصنيف المنتج" />
                  </SelectTrigger>
                  <SelectContent className="glass rounded-xl">
                    {categories?.results?.map((cat: any) => (
                      <SelectItem key={cat.id} value={cat.id.toString()} className="text-right justify-end">{cat.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-semibold">وصف المنتج</Label>
              <Textarea 
                value={form.description} onChange={e => updateForm('description', e.target.value)}
                placeholder="اشرح مميزات المنتج، المواد المستخدمة، المقاسات المتوفرة..."
                className="min-h-[140px] rounded-xl bg-white/5 border-white/10 text-right resize-none"
              />
              <p className="text-[11px] text-muted-foreground">{form.description.length}/1000 حرف</p>
            </div>

            <div className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
              <input 
                type="checkbox" checked={form.is_featured}
                onChange={e => updateForm('is_featured', e.target.checked)}
                className="w-5 h-5 rounded accent-blue-500"
              />
              <div>
                <p className="font-medium flex items-center gap-2">
                  <Star className="w-4 h-4 text-yellow-400" /> تمييز كمنتج بارز
                </p>
                <p className="text-xs text-muted-foreground">سيظهر المنتج في القسم المميز بالصفحة الرئيسية</p>
              </div>
            </div>
          </div>
        )}

        {/* ── Step 2: Pricing ── */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold">التسعير والمخزون</h2>
                <p className="text-sm text-muted-foreground">حدد سعر المنتج والكمية المتوفرة</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-semibold">السعر (دج) <span className="text-red-400">*</span></Label>
                <div className="relative">
                  <Input 
                    type="number" value={form.price} onChange={e => updateForm('price', e.target.value)}
                    placeholder="0.00" className="h-12 rounded-xl bg-white/5 border-white/10 text-right pl-12"
                  />
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground font-medium">د.ج</span>
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-semibold">سعر التخفيض</Label>
                <div className="relative">
                  <Input 
                    type="number" value={form.discount_price} onChange={e => updateForm('discount_price', e.target.value)}
                    placeholder="اتركه فارغاً إذا لا يوجد" className="h-12 rounded-xl bg-white/5 border-white/10 text-right pl-12"
                  />
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground font-medium">د.ج</span>
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-semibold">الكمية المتوفرة <span className="text-red-400">*</span></Label>
                <Input 
                  type="number" value={form.stock} onChange={e => updateForm('stock', e.target.value)}
                  placeholder="مثلاً: 50" className="h-12 rounded-xl bg-white/5 border-white/10 text-right"
                />
              </div>
            </div>

            {/* Price Preview */}
            {form.price && (
              <div className="p-6 rounded-2xl bg-gradient-to-l from-blue-500/10 to-violet-500/10 border border-blue-500/20">
                <p className="text-sm text-muted-foreground mb-2">معاينة السعر للعميل</p>
                <div className="flex items-baseline gap-3">
                  {form.discount_price ? (
                    <>
                      <span className="text-3xl font-black text-emerald-400">
                        {new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(form.discount_price))}
                      </span>
                      <span className="text-lg line-through text-muted-foreground">
                        {new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(form.price))}
                      </span>
                      <span className="px-2 py-1 rounded-lg bg-red-500/20 text-red-400 text-xs font-bold">
                        -{Math.round((1 - Number(form.discount_price) / Number(form.price)) * 100)}%
                      </span>
                    </>
                  ) : (
                    <span className="text-3xl font-black">
                      {new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(form.price))}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Step 3: Media ── */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-violet-500/20 flex items-center justify-center">
                <ImageIcon className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold">الصور والوسائط</h2>
                <p className="text-sm text-muted-foreground">أضف صوراً عالية الجودة لمنتجك</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Main Image */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold flex items-center gap-2">
                  <Star className="w-3 h-3 text-yellow-400" /> الصورة الأساسية
                </Label>
                <div 
                  className={cn("aspect-square upload-zone rounded-2xl relative overflow-hidden", mainImage && "border-blue-500")}
                  onClick={() => document.getElementById('main-img')?.click()}
                  onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={e => {
                    e.preventDefault(); e.stopPropagation(); setDragActive(false)
                    const f = e.dataTransfer.files[0]
                    if (f?.type.startsWith('image/')) setMainImage(f)
                  }}
                >
                  {mainImage ? (
                    <>
                      <img src={URL.createObjectURL(mainImage)} className="w-full h-full object-cover" alt="" />
                      <div className="absolute inset-0 bg-black/50 opacity-0 hover:opacity-100 flex items-center justify-center transition-opacity">
                        <p className="text-white font-medium text-sm">انقر لتغيير الصورة</p>
                      </div>
                      <button
                        type="button"
                        onClick={e => { e.stopPropagation(); setMainImage(null) }}
                        className="absolute top-3 left-3 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center text-white shadow-lg hover:bg-red-600 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                      <span className="absolute bottom-3 right-3 px-3 py-1 bg-blue-500 text-white text-xs rounded-full font-medium">
                        الصورة الأساسية
                      </span>
                    </>
                  ) : (
                    <div className="flex flex-col items-center gap-3 p-8">
                      <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                        <Upload className="w-8 h-8 text-blue-400" />
                      </div>
                      <p className="font-medium">اسحب الصورة هنا أو انقر للرفع</p>
                      <p className="text-xs text-muted-foreground">PNG, JPG, WEBP • حتى 5MB</p>
                    </div>
                  )}
                  <input type="file" id="main-img" className="hidden" accept="image/*"
                    onChange={e => e.target.files?.[0] && setMainImage(e.target.files[0])}
                  />
                </div>
              </div>

              {/* Gallery */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold flex items-center justify-between">
                  <span>معرض الصور</span>
                  <span className="text-xs text-muted-foreground font-normal">{galleryImages.length}/5 صور</span>
                </Label>
                <div 
                  className={cn("grid grid-cols-2 gap-3 min-h-[200px]", dragActive && "ring-2 ring-blue-500/50 rounded-2xl")}
                  onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                >
                  {galleryImages.map((img, i) => (
                    <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-white/10 group">
                      <img src={URL.createObjectURL(img)} className="w-full h-full object-cover" alt="" />
                      <button
                        type="button" onClick={() => removeGalleryImage(i)}
                        className="absolute top-2 left-2 w-7 h-7 bg-red-500 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                  {galleryImages.length < 5 && (
                    <div 
                      className="aspect-square upload-zone rounded-xl"
                      onClick={() => document.getElementById('gallery-imgs')?.click()}
                    >
                      <Plus className="w-6 h-6 text-muted-foreground" />
                      <p className="text-xs text-muted-foreground mt-1">إضافة صورة</p>
                      <input type="file" id="gallery-imgs" className="hidden" accept="image/*" multiple
                        onChange={e => {
                          if (e.target.files) {
                            setGalleryImages(prev => [...prev, ...Array.from(e.target.files!)].slice(0, 5))
                          }
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Step 4: Review ── */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                <Check className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold">المراجعة والنشر</h2>
                <p className="text-sm text-muted-foreground">راجع بيانات المنتج قبل النشر</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-1">اسم المنتج</p>
                  <p className="font-bold text-lg">{form.name || '—'}</p>
                </div>
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-1">الوصف</p>
                  <p className="text-sm">{form.description || 'لم يتم إضافة وصف'}</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                    <p className="text-xs text-muted-foreground mb-1">السعر</p>
                    <p className="font-bold text-blue-400">{form.price ? `${form.price} د.ج` : '—'}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                    <p className="text-xs text-muted-foreground mb-1">المخزون</p>
                    <p className="font-bold">{form.stock || '—'} قطعة</p>
                  </div>
                </div>
              </div>
              <div>
                {mainImage ? (
                  <img src={URL.createObjectURL(mainImage)} className="w-full aspect-square object-cover rounded-2xl border border-white/10" alt="" />
                ) : (
                  <div className="w-full aspect-square rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                    <p className="text-muted-foreground">لا توجد صورة</p>
                  </div>
                )}
                {galleryImages.length > 0 && (
                  <div className="flex gap-2 mt-3">
                    {galleryImages.map((img, i) => (
                      <img key={i} src={URL.createObjectURL(img)} className="w-14 h-14 rounded-lg object-cover border border-white/10" alt="" />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between glass-card border-none p-4">
        <Button
          variant="ghost" onClick={() => currentStep > 0 ? setCurrentStep(currentStep - 1) : navigate('/products')}
          className="rounded-xl gap-2"
        >
          {currentStep === 0 ? 'إلغاء' : 'السابق'}
        </Button>
        
        {currentStep < STEPS.length - 1 ? (
          <Button onClick={() => setCurrentStep(currentStep + 1)} className="rounded-xl gap-2 bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20">
            التالي <Layers className="w-4 h-4" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={loading} className="rounded-xl gap-2 bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 min-w-[160px]">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
            <span>نشر المنتج</span>
          </Button>
        )}
      </div>
    </div>
  )
}
