import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { APP_GUARD } from '@nestjs/core';
import { ScheduleModule } from '@nestjs/schedule';

import { PrismaModule } from './prisma/prisma.module';
import { AuthModule } from './modules/auth/auth.module';
import { UsersModule } from './modules/users/users.module';
import { CompaniesModule } from './modules/companies/companies.module';
import { ClientsModule } from './modules/clients/clients.module';
import { CarriersModule } from './modules/carriers/carriers.module';
import { BranchesModule } from './modules/branches/branches.module';
import { ContractsModule } from './modules/contracts/contracts.module';
import { DocumentsModule } from './modules/documents/documents.module';
import { DiscrepanciesModule } from './modules/discrepancies/discrepancies.module';
import { ContestsModule } from './modules/contests/contests.module';
import { ReportsModule } from './modules/reports/reports.module';
import { NotificationsModule } from './modules/notifications/notifications.module';
import { AuditModule } from './modules/audit/audit.module';
import { HealthModule } from './modules/health/health.module';

@Module({
  imports: [
    // Configuration
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env.local', '.env'],
      cache: true,
    }),

    // Rate limiting
    ThrottlerModule.forRoot([
      {
        ttl: 60000, // 1 minute
        limit: 100, // 100 requests per minute
      },
    ]),

    // Scheduling for background jobs
    ScheduleModule.forRoot(),

    // Core modules
    PrismaModule,
    AuthModule,
    UsersModule,
    CompaniesModule,
    ClientsModule,
    CarriersModule,
    BranchesModule,
    ContractsModule,
    DocumentsModule,
    DiscrepanciesModule,
    ContestsModule,
    ReportsModule,
    NotificationsModule,
    AuditModule,
    HealthModule,
  ],
  providers: [
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}