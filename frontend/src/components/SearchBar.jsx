import { useState } from 'react'
import { Search, Clock } from 'lucide-react'

function SearchBar({ onSearch, setResult }) {
  const [query, setQuery] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (query.trim()) {
      await onSearch(query)
      setQuery('')
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What do you want to know?"
            className="w-full bg-gray-800 text-white px-4 py-3 pr-12 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00A3BF]"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2 text-gray-400">
            <Search size={18} className="cursor-pointer" onClick={handleSubmit} />
            <span className="text-sm cursor-pointer" onClick={() => setResult(null)}>Clear</span>
          </div>
        </div>
      </form>
    </div>
  )
}

export default SearchBar