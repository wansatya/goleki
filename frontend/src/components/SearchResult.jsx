import { Sparkles, ExternalLink } from 'lucide-react'

function formatAnswer(answer) {
  if (!answer) return null

  // Split into paragraphs and filter out empty ones
  const paragraphs = answer
    .split('\n')
    .filter(p => p.trim() !== '')
    .map(p => p.trim())

  return (
    <div className="space-y-5">
      {paragraphs.map((paragraph, index) => {
        // Check if it's a list item
        if (paragraph.startsWith('•') || paragraph.startsWith('-')) {
          return (
            <ul key={index} className="list-disc list-inside">
              <li className="text-[#ececec] leading-7">
                {paragraph.substring(1).trim()}
              </li>
            </ul>
          )
        }

        // Check if it's a heading (starts with '#')
        if (paragraph.startsWith('#')) {
          return (
            <h3 key={index} className="text-lg font-semibold text-[#ececec] mt-6 mb-3">
              {paragraph.replace(/^#+\s/, '')}
            </h3>
          )
        }

        // Regular paragraph
        return (
          <p key={index} className="text-[#ececec] leading-7">
            {paragraph}
          </p>
        )
      })}
    </div>
  )
}

function SearchResult({ query, result, isSearching }) {
  if (!result && !isSearching) return null

  return (
    <div className="py-4">
      {/* Query Title */}
      <h1 className="text-2xl font-semibold mb-6">{query}</h1>

      {/* Sources Section */}
      <div className="mb-6">
        {!isSearching && <h2 className="text-lg font-semibold mb-4 flex items-center">
          <span className="mr-2">Sources</span>
          <div className="flex items-center space-x-1">
            {result?.sources?.map((source, i) => (
              <SourceIcon key={i} index={i + 1} url={source.url} />
            ))}
          </div>
        </h2>}

        {/* Source Links */}
        <div className="space-y-4">
          {!isSearching && result?.sources?.map((source, i) => (
            <SourceLink
              key={i}
              title={source.title}
              url={source.url}
              index={i + 1}
            />
          ))}
        </div>
      </div>

      {/* Answer Section */}
      {isSearching ? (
        <SourcesSkeleton />
      ) : (
        <div className="text-[#ececec]">
          <Sparkles className="w-5 h-5 text-[#686b6e]" /> <span>{formatAnswer(result?.answer)}</span>
          <br /><small className="italic text-gray-500">ready in {result?.processing_time.toFixed(2)} secs.</small>
        </div>
      )}

    </div>
  )
}

function SourceIcon({ index, url }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="w-6 h-6 flex items-center justify-center bg-gray-800 rounded-full text-xs hover:bg-gray-700"
    >
      {index}
    </a>
  )
}

function SourceLink({ title, url, index }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="block p-4 bg-gray-800 rounded-lg hover:bg-gray-700"
    >
      <div className="flex items-start space-x-3">
        <span className="text-gray-400">{index}</span>
        <div className="flex-1">
          <h3 className="font-medium">{title}</h3>
          <p className="text-gray-400 text-sm truncate">{url}</p>
        </div>
        <ExternalLink size={16} className="text-gray-400" />
      </div>
    </a>
  )
}

function SourcesSkeleton() {
  return (
    <div className="space-y-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="p-3 bg-[#1a1b1e] rounded animate-pulse">
          <div className="flex items-start gap-3">
            <div className="w-4 h-4 bg-[#242628] rounded" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-[#242628] rounded w-3/4" />
              <div className="h-3 bg-[#242628] rounded w-1/2" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default SearchResult