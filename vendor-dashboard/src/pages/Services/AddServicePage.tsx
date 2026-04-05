import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  ArrowRight, Upload, X, Image as ImageIcon, Plus, Star,
  Briefcase, DollarSign, MapPin, FileText, Loader2, Check, Clock, Search
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
import { Badge } from '../../components/ui/badge'
import { cn } from '../../lib/utils'

const STEPS = [
  { id: 'info',     label: 'معلومات الخدمة', icon: FileText },
  { id: 'pricing',  label: 'التسعير والتغطية', icon: DollarSign },
  { id: 'media',    label: 'صور الأعمال',    icon: ImageIcon },
  { id: 'review',   label: 'المراجعة والنشر', icon: Check },
]

export default function AddServicePage() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [mainImage, setMainImage] = useState<File | null>(null)
  const [galleryImages, setGalleryImages] = useState<File[]>([])
  const [selectedWilayas, setSelectedWilayas] = useState<string[]>([])
  const [wilayaSearch, setWilayaSearch] = useState('')

  const [form, setForm] = useState({
    name: '', description: '', category: '', 
    price: '', duration: '',
  })

  const { data: categories } = useQuery({
    queryKey: ['service-categories'],
    queryFn: () => generalClient.get('/services/categories/').then(r => r.data)
  })

  const { data: wilayas } = useQuery({
    queryKey: ['wilayas'],
    queryFn: () => generalClient.get('/localization/wilayas/').then(r => r.data)
  })

  const updateForm = (field: string, value: any) => setForm(prev => ({ ...prev, [field]: value }))

  const filteredWilayas = (wilayas || []).filter((w: any) => 
    w.name.includes(wilayaSearch) && !selectedWilayas.includes(w.id.toString())
  )

  const toggleAllWilayas = () => {
    if (selectedWilayas.length === (wilayas?.length || 0)) {
      setSelectedWilayas([])
    } else {
      setSelectedWilayas((wilayas || []).map((w: any) => w.id.toString()))
    }
  }

  const removeGalleryImage = (idx: number) => setGalleryImages(prev => prev.filter((_, i) => i !== idx))

  const completion = Math.round(
    ([form.name, form.category, form.description, form.price, selectedWilayas.length > 0, mainImage].filter(Boolean).length / 6) * 100
  )

  const handleSubmit = async () => {
    if (!form.name || !form.category || !form.price) {
      toast.error('يرجى ملء جميع الحقول المطلوبة')
      return
    }
    setLoading(true)
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('description', form.description)
    formData.append('category', form.category)
    formData.append('price', form.price)
    if (mainImage) formData.append('image_main', mainImage)
    selectedWilayas.forEach(w => formData.append('wilayas', w))
    galleryImages.forEach(img => formData.append('uploaded_images', img))

    try {
      await apiClient.post('/services/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      toast.success('تمت إضافة الخدمة بنجاح! 🎉')
      navigate('/services')
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
          <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => navigate('/services')}>
            <ArrowRight className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-black">إضافة خدمة جديدة</h1>
            <p className="text-muted-foreground text-sm mt-1">قدّم خدماتك لآلاف العملاء عبر المنصة</p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-3">
          <div className="text-left">
            <p className="text-xs text-muted-foreground">اكتمال النموذج</p>
            <p className="text-lg font-bold text-emerald-400">{completion}%</p>
          </div>
          <div className="w-16 h-16 relative">
            <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="2" className="text-white/5" />
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray={`${completion}, 100`} className="text-emerald-500" strokeLinecap="round" />
            </svg>
            <Briefcase className="w-5 h-5 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-emerald-400" />
          </div>
        </div>
      </div>

      {/* Step Indicators */}
      <div className="glass-card border-none p-4">
        <div className="flex items-center justify-between">
          {STEPS.map((step, idx) => (
            <button key={step.id} onClick={() => setCurrentStep(idx)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all text-sm font-medium flex-1 justify-center",
                idx === currentStep ? "bg-emerald-500/20 text-emerald-400" : idx < currentStep ? "text-emerald-400 bg-emerald-500/10" : "text-muted-foreground hover:bg-white/5"
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
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center"><FileText className="w-5 h-5 text-emerald-400" /></div>
              <div>
                <h2 className="text-xl font-bold">معلومات الخدمة</h2>
                <p className="text-sm text-muted-foreground">حدد نوع الخدمة وتفاصيلها</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-semibold">اسم الخدمة <span className="text-red-400">*</span></Label>
                <Input value={form.name} onChange={e => updateForm('name', e.target.value)} placeholder="مثلاً: صيانة أجهزة كهرومنزلية" className="h-12 rounded-xl bg-white/5 border-white/10 text-right" />
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-semibold">التصنيف <span className="text-red-400">*</span></Label>
                <Select value={form.category} onValueChange={v => updateForm('category', v)}>
                  <SelectTrigger className="h-12 rounded-xl bg-white/5 border-white/10 text-right"><SelectValue placeholder="اختر تصنيف الخدمة" /></SelectTrigger>
                  <SelectContent className="glass rounded-xl">
                    {categories?.results?.map((cat: any) => (
                      <SelectItem key={cat.id} value={cat.id.toString()} className="text-right justify-end">{cat.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-sm font-semibold">وصف الخدمة</Label>
              <Textarea value={form.description} onChange={e => updateForm('description', e.target.value)} placeholder="اشرح ما تتضمنه الخدمة، الخبرة، الضمانات..." className="min-h-[140px] rounded-xl bg-white/5 border-white/10 text-right resize-none" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-semibold flex items-center gap-2"><Clock className="w-3 h-3" /> مدة التنفيذ المتوقعة</Label>
                <Input value={form.duration} onChange={e => updateForm('duration', e.target.value)} placeholder="مثلاً: 2-3 أيام عمل" className="h-12 rounded-xl bg-white/5 border-white/10 text-right" />
              </div>
            </div>
          </div>
        )}

        {/* ── Step 2: Pricing & Coverage ── */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center"><DollarSign className="w-5 h-5 text-blue-400" /></div>
              <div>
                <h2 className="text-xl font-bold">التسعير ومناطق التغطية</h2>
                <p className="text-sm text-muted-foreground">حدد سعر الخدمة والولايات التي تُقدَّم فيها</p>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-semibold">السعر الابتدائي (دج) <span className="text-red-400">*</span></Label>
              <div className="relative max-w-xs">
                <Input type="number" value={form.price} onChange={e => updateForm('price', e.target.value)} placeholder="0.00" className="h-12 rounded-xl bg-white/5 border-white/10 text-right pl-12" />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">د.ج</span>
              </div>
            </div>

            {/* Wilayas Selection */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-semibold flex items-center gap-2"><MapPin className="w-3 h-3 text-emerald-400" /> مناطق التغطية (الولايات)</Label>
                <Button type="button" variant="ghost" size="sm" onClick={toggleAllWilayas} className="text-xs rounded-lg">
                  {selectedWilayas.length === (wilayas?.length || 0) ? 'إلغاء الكل' : 'تحديد الكل (48 ولاية)'}
                </Button>
              </div>
              
              {/* Selected Wilayas */}
              <div className="flex flex-wrap gap-2 p-3 rounded-xl bg-white/5 border border-white/10 min-h-[48px]">
                {selectedWilayas.length === 0 && <span className="text-xs text-muted-foreground">لم يتم تحديد أي ولاية بعد...</span>}
                {selectedWilayas.map(id => {
                  const w = (wilayas || []).find((x: any) => x.id.toString() === id)
                  return (
                    <Badge key={id} variant="secondary" className="gap-1 px-2 py-1 bg-emerald-500/10 text-emerald-400 border-emerald-500/20 rounded-lg">
                      {w?.name}
                      <X className="w-3 h-3 cursor-pointer hover:text-red-400" onClick={() => setSelectedWilayas(selectedWilayas.filter(x => x !== id))} />
                    </Badge>
                  )
                })}
              </div>

              {/* Search & Add Wilayas */}
              <div className="relative">
                <Search className="absolute right-3 top-3 w-4 h-4 text-muted-foreground" />
                <Input value={wilayaSearch} onChange={e => setWilayaSearch(e.target.value)} placeholder="ابحث عن ولاية..." className="pr-10 rounded-xl bg-white/5 border-white/10 text-right" />
              </div>
              <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-[200px] overflow-y-auto p-1">
                {filteredWilayas.map((w: any) => (
                  <button key={w.id} type="button"
                    onClick={() => setSelectedWilayas([...selectedWilayas, w.id.toString()])}
                    className="text-xs px-3 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-emerald-500/10 hover:border-emerald-500/30 hover:text-emerald-400 transition-all text-center truncate"
                  >
                    {w.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── Step 3: Media ── */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-violet-500/20 flex items-center justify-center"><ImageIcon className="w-5 h-5 text-violet-400" /></div>
              <div>
                <h2 className="text-xl font-bold">صور الخدمة</h2>
                <p className="text-sm text-muted-foreground">أضف صورة رئيسية وصوراً توضيحية لأعمالك</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Main Image */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold flex items-center gap-2">
                  <Star className="w-3 h-3 text-yellow-400" /> الصورة الأساسية للخدمة
                </Label>
                <div 
                  className={cn("aspect-square upload-zone rounded-2xl relative overflow-hidden", mainImage && "border-emerald-500")}
                  onClick={() => document.getElementById('srv-main-img')?.click()}
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
                      <span className="absolute bottom-3 right-3 px-3 py-1 bg-emerald-500 text-white text-xs rounded-full font-medium">
                        الصورة الأساسية
                      </span>
                    </>
                  ) : (
                    <div className="flex flex-col items-center gap-3 p-8">
                      <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                        <Upload className="w-8 h-8 text-emerald-400" />
                      </div>
                      <p className="font-medium">اسحب الصورة هنا أو انقر للرفع</p>
                      <p className="text-xs text-muted-foreground">PNG, JPG, WEBP • حتى 5MB</p>
                    </div>
                  )}
                  <input type="file" id="srv-main-img" className="hidden" accept="image/*"
                    onChange={e => e.target.files?.[0] && setMainImage(e.target.files[0])}
                  />
                </div>
              </div>

              {/* Gallery */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold flex items-center justify-between">
                  <span>معرض الأعمال السابقة</span>
                  <span className="text-xs text-muted-foreground font-normal">{galleryImages.length}/5 صور</span>
                </Label>
                <div className="grid grid-cols-2 gap-3 min-h-[200px]">
                  {galleryImages.map((img, i) => (
                    <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-white/10 group">
                      <img src={URL.createObjectURL(img)} className="w-full h-full object-cover" alt="" />
                      <button type="button" onClick={() => removeGalleryImage(i)}
                        className="absolute top-2 left-2 w-7 h-7 bg-red-500 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                      ><X className="w-3 h-3" /></button>
                    </div>
                  ))}
                  {galleryImages.length < 5 && (
                    <div className="aspect-square upload-zone rounded-xl" onClick={() => document.getElementById('srv-imgs')?.click()}>
                      <Plus className="w-6 h-6 text-muted-foreground" />
                      <p className="text-xs text-muted-foreground mt-1">إضافة صورة</p>
                      <input type="file" id="srv-imgs" className="hidden" accept="image/*" multiple
                        onChange={e => e.target.files && setGalleryImages(prev => [...prev, ...Array.from(e.target.files!)].slice(0, 5))}
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
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center"><Check className="w-5 h-5 text-emerald-400" /></div>
              <div><h2 className="text-xl font-bold">المراجعة والنشر</h2><p className="text-sm text-muted-foreground">راجع بيانات الخدمة قبل النشر</p></div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-white/5 border border-white/10"><p className="text-xs text-muted-foreground mb-1">اسم الخدمة</p><p className="font-bold text-lg">{form.name || '—'}</p></div>
              <div className="p-4 rounded-xl bg-white/5 border border-white/10"><p className="text-xs text-muted-foreground mb-1">السعر الابتدائي</p><p className="font-bold text-lg text-emerald-400">{form.price ? `${form.price} د.ج` : '—'}</p></div>
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 col-span-2"><p className="text-xs text-muted-foreground mb-1">الوصف</p><p className="text-sm">{form.description || 'لم يتم إضافة وصف'}</p></div>
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 col-span-2">
                <p className="text-xs text-muted-foreground mb-2">مناطق التغطية ({selectedWilayas.length} ولاية)</p>
                <div className="flex flex-wrap gap-1">
                  {selectedWilayas.map(id => {
                    const w = (wilayas || []).find((x: any) => x.id.toString() === id)
                    return <Badge key={id} variant="secondary" className="text-[10px] bg-emerald-500/10 text-emerald-400">{w?.name}</Badge>
                  })}
                </div>
              </div>
            </div>
            {/* Image preview in review */}
            <div className="grid grid-cols-2 gap-4">
              {mainImage && (
                <div>
                  <p className="text-xs text-muted-foreground mb-2">الصورة الأساسية</p>
                  <img src={URL.createObjectURL(mainImage)} className="w-full aspect-video object-cover rounded-xl border border-emerald-500/30" alt="" />
                </div>
              )}
              {galleryImages.length > 0 && (
                <div>
                  <p className="text-xs text-muted-foreground mb-2">معرض الأعمال ({galleryImages.length} صور)</p>
                  <div className="flex gap-2 overflow-x-auto">
                    {galleryImages.map((img, i) => <img key={i} src={URL.createObjectURL(img)} className="w-20 h-14 rounded-lg object-cover border border-white/10 flex-shrink-0" alt="" />)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between glass-card border-none p-4">
        <Button variant="ghost" onClick={() => currentStep > 0 ? setCurrentStep(currentStep - 1) : navigate('/services')} className="rounded-xl gap-2">
          {currentStep === 0 ? 'إلغاء' : 'السابق'}
        </Button>
        {currentStep < STEPS.length - 1 ? (
          <Button onClick={() => setCurrentStep(currentStep + 1)} className="rounded-xl gap-2 bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-500/20">التالي</Button>
        ) : (
          <Button onClick={handleSubmit} disabled={loading} className="rounded-xl gap-2 bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 min-w-[160px]">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
            <span>نشر الخدمة</span>
          </Button>
        )}
      </div>
    </div>
  )
}
