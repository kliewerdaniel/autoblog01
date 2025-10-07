'use client';

import Image from 'next/image';
import { useState } from 'react';

interface ArtPiece {
  id: string;
  title: string;
  src: string;
  alt: string;
  year?: string;
  medium?: string;
  description?: string;
}

interface ArtGridProps {
  artPieces: ArtPiece[];
}

export default function ArtGrid({ artPieces }: ArtGridProps) {
  const [selectedPiece, setSelectedPiece] = useState<ArtPiece | null>(null);

  if (artPieces.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No artwork found</h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Art gallery will be populated with new pieces soon.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {artPieces.map((piece) => (
          <div
            key={piece.id}
            className="group cursor-pointer"
            onClick={() => setSelectedPiece(piece)}
          >
            <div className="relative aspect-square overflow-hidden rounded-lg bg-gray-100">
              <Image
                src={piece.src}
                alt={piece.alt}
                fill
                className="object-cover z-10"
                style={{
                  filter: 'none',
                  WebkitFilter: 'none',
                  imageRendering: 'auto'
                }}
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                onError={() => console.error('Image failed to load:', piece.src)}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Lightbox Modal */}
      {selectedPiece && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-75"
          onClick={() => setSelectedPiece(null)}
        >
          <div
            className="relative max-w-4xl max-h-full bg-white dark:bg-gray-900 rounded-lg overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative aspect-video">
              <Image
                src={selectedPiece.src}
                alt={selectedPiece.alt}
                fill
                className="object-contain"
                sizes="100vw"
              />
            </div>
            <div className="p-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {selectedPiece.title}
              </h3>
              <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
                {selectedPiece.year && <span>Year: {selectedPiece.year}</span>}
                {selectedPiece.medium && <span>Medium: {selectedPiece.medium}</span>}
              </div>
              {selectedPiece.description && (
                <p className="text-gray-700 dark:text-gray-300">
                  {selectedPiece.description}
                </p>
              )}
            </div>
            <button
              onClick={() => setSelectedPiece(null)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
}
