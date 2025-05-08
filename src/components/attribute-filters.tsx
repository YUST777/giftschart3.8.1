import { useState, useEffect } from 'react'
import { useAppState } from '@/lib/state'
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { getCollectionData } from '@/lib/api'
import { toast } from 'sonner'

const encode = encodeURIComponent

export function AttributeFilters() {
  const { state, dispatch } = useAppState()
  const [isLoading, setIsLoading] = useState(false)
  const [giftId, setGiftId] = useState('')

  // Extract option lists from attributesWithPercentages
  const traitOptions = (trait: string) => {
    const t = Object.keys(state.attributesWithPercentages).find(k => k.toLowerCase() === trait.toLowerCase())
    if (!t) return []
    return Object.keys(state.attributesWithPercentages[t] || {})
  }

  const handleTraitChange = async (trait: string, value: string) => {
    if (!state.collectionData?.giftName) return
    const newFilters = { ...state.filters.attributes }
    if (value === 'All') {
      delete newFilters[trait]
    } else {
      newFilters[trait] = [value]
    }
    await applyFilters(newFilters)
  }

  const applyFilters = async (attributes: Record<string, string[]>) => {
    if (!state.collectionData?.giftName) return
    setIsLoading(true)
    try {
      dispatch({ type: 'SET_FILTERS', payload: { attributes } })
      const result = await getCollectionData(
        state.collectionData.giftName,
        1,
        state.itemsPerPage,
        { attributes },
        state.sortOption,
        true
      )
      dispatch({ type: 'SET_COLLECTION_DATA', payload: result.collectionData })
      dispatch({ type: 'SET_CURRENT_PAGE', payload: 1 })
      if (Object.keys(result.attributes).length)
        dispatch({ type: 'SET_ATTRIBUTES_WITH_PERCENTAGES', payload: result.attributes })
    } catch (e) {
      toast.error((e as Error).message)
    } finally {
      setIsLoading(false)
    }
  }

  const getPreviewUrl = (trait: string, value: string) => {
    if (!state.collectionData?.giftName) return ''
    const collection = encode(state.collectionData.giftName.toLowerCase())
    const encodedValue = encode(value)
    if (trait.toLowerCase() === 'model') {
      return `https://gifts.coffin.meme/${collection}/${encodedValue}.png`
    }
    if (trait.toLowerCase() === 'symbol') {
      return `https://gifts.coffin.meme/patterns/${encodedValue}.tgs?v=3`
    }
    return ''
  }

  const applyGiftId = async () => {
    if (!giftId.trim()) return
    if (!state.collectionData?.giftName) return
    const attrs = { ...state.filters.attributes }
    attrs['ID'] = [giftId.trim()]
    await applyFilters(attrs)
  }

  const clearFilters = () => applyFilters({})

  const triggerCls =
    'h-[56px] w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-[#1c1c1d] px-3 py-1 text-xs text-gray-800 dark:text-gray-100 flex flex-col items-start justify-center gap-0.5 shadow-sm'

  return (
    <div className="w-full bg-white dark:bg-[#1c1c1d] rounded-xl p-3 grid grid-cols-3 gap-3">
      {/* Model */}
      <div className="col-span-1 flex flex-col">
        <Select
          onValueChange={(v) => handleTraitChange('Model', v)}
          defaultValue={state.filters.attributes['Model']?.[0] ?? 'All'}
        >
          <SelectTrigger className={triggerCls}>
            <span className="text-[11px] text-gray-500 dark:text-gray-400 font-medium">Model</span>
            <SelectValue placeholder="Model" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="All">All</SelectItem>
              {traitOptions('Model').map((opt) => (
                <SelectItem key={opt} value={opt}>
                  <div className="flex items-center gap-2">
                    <img src={getPreviewUrl('Model', opt)} alt={opt} className="w-5 h-5 object-contain" />
                    {opt}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
      {/* Backdrop */}
      <div className="col-span-1 flex flex-col">
        <Select
          onValueChange={(v) => handleTraitChange('Backdrop', v)}
          defaultValue={state.filters.attributes['Backdrop']?.[0] ?? 'All'}
        >
          <SelectTrigger className={triggerCls}>
            <span className="text-[11px] text-gray-500 dark:text-gray-400 font-medium">Backdrop</span>
            <SelectValue placeholder="Backdrop" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="All">All</SelectItem>
              {traitOptions('Backdrop').map((opt) => (
                <SelectItem key={opt} value={opt}>{opt}</SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
      {/* Symbol */}
      <div className="col-span-1 flex flex-col">
        <Select
          onValueChange={(v) => handleTraitChange('Symbol', v)}
          defaultValue={state.filters.attributes['Symbol']?.[0] ?? 'All'}
        >
          <SelectTrigger className={triggerCls}>
            <span className="text-[11px] text-gray-500 dark:text-gray-400 font-medium">Symbol</span>
            <SelectValue placeholder="Symbol" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="All">All</SelectItem>
              {traitOptions('Symbol').map((opt) => (
                <SelectItem key={opt} value={opt}>
                  <div className="flex items-center gap-2">
                    <img src={getPreviewUrl('Symbol', opt)} alt={opt} className="w-5 h-5 object-contain" />
                    {opt}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
      {/* Gift ID input */}
      <div className="col-span-2 flex items-center gap-2 mt-1">
        <Input
          placeholder="#"
          value={giftId}
          onChange={(e) => setGiftId(e.target.value)}
          className="h-[56px] rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-[#1c1c1d] px-3 py-1 text-xs text-gray-800 dark:text-gray-100 flex-1 shadow-sm"
        />
        <Button
          size="sm"
          onClick={applyGiftId}
          disabled={isLoading}
          className="h-[40px] px-5 rounded-lg bg-black text-white dark:bg-white dark:text-black font-semibold text-xs shadow-sm hover:bg-gray-900 dark:hover:bg-gray-200 transition"
        >
          Go
        </Button>
      </div>
      {/* Trash / Clear */}
      <div className="col-span-1 flex items-center justify-end mt-1">
        <Button
          variant="outline"
          onClick={clearFilters}
          disabled={isLoading}
          className="h-[40px] w-[56px] rounded-lg flex items-center justify-center border border-gray-300 dark:border-gray-700 bg-white dark:bg-[#1c1c1d] shadow-sm hover:bg-gray-100 dark:hover:bg-[#232324] transition"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M9 3v1H4v2h1v14a2 2 0 002 2h10a2 2 0 002-2V6h1V4h-5V3H9zm2 4h2v12h-2V7z"/>
          </svg>
        </Button>
      </div>
    </div>
  )
}
